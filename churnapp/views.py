from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import joblib
import os
from django.conf import settings
import numpy as np
from .models import ChurnPrediction   # make sure model exists
from django.http import JsonResponse
from django.db.models import Count

import csv
from io import TextIOWrapper


# Load ML files safely
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_model', 'churn_model.pkl')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'ml_model', 'scaler.pkl')

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):

    customers = ChurnPrediction.objects.all()
    total_customers = customers.count()

    # High risk customers (Churn = 1)
    high_risk_customers = customers.filter(prediction=1)
    high_risk = high_risk_customers.count()

    # Risk distribution
    low = customers.filter(prediction=0).count()

    # Metrics
    retention_rate = round((low / total_customers) * 100, 2) if total_customers > 0 else 0
    monthly_revenue = 285  # static demo value

    context = {
        'total_customers': total_customers,
        'high_risk': high_risk,
        'retention_rate': retention_rate,
        'monthly_revenue': monthly_revenue,

        'total_growth': 12,
        'high_risk_change': "-8%",
        'retention_change': 2.4,
        'revenue_change': 5.2,

        'low_risk': low,
        'high_risk_customers': high_risk_customers,
    }

    return render(request, 'dashboard.html', context)


# ==========================
# OTHER PAGES
# ==========================
@login_required
def customers_view(request):
    query = request.GET.get('q')  # get search value from URL

    customers = ChurnPrediction.objects.all().order_by('-id')

    if query:
        customers = customers.filter(customer_id__icontains=query)

    return render(request, 'customers.html', {'customers': customers})



@login_required
def add_customer_view(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        country = request.POST.get("country")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        balance = request.POST.get("balance")

        print(customer_id, country, gender, age, balance)  # debug

        ChurnPrediction.objects.update_or_create(
            customer_id=customer_id,
            defaults={
                'country': country,
                'gender': gender,
                'age': age,
                'balance': balance,
                'credit_score': 600,
                'tenure': 1,
                'num_products': 1,
                'has_card': 1,
                'is_active': 1,
                'salary': 50000.0,
                'prediction': 0,
                'probability': 0.0
            }
        )

        return redirect('customers')

    return render(request, 'add_customer.html')

def upload_data_view(request):
    return render(request, 'upload_data.html')


# ==========================
# PREDICTION
# ==========================
@login_required
def predict_churn(request):
    result = None
    proba = 0
    form_data = {}
    suggestions = []   

    if request.method == 'POST':
        customer_id = request.POST['customer_id']

        # Get form data
        credit_score = int(request.POST['credit_score'])
        country = request.POST['country']
        gender = request.POST['gender']
        age = int(request.POST['age'])
        tenure = int(request.POST['tenure'])
        balance = float(request.POST['balance'])
        num_products = int(request.POST['num_products'])
        has_card = int(request.POST['has_card'])
        is_active = int(request.POST['is_active'])
        salary = float(request.POST['salary'])

        form_data = {
            'credit_score': credit_score,
            'country': country,
            'gender': gender,
            'age': age,
            'tenure': tenure,
            'balance': balance,
            'num_products': num_products,
            'has_card': has_card,
            'is_active': is_active,
            'salary': salary,
        }

        # Encode categorical values
        gender_encoded = 1 if gender == 'Male' else 0
        country_encoded = {'France': 0, 'Germany': 1, 'Spain': 2}[country]

        features = np.array([[  
            credit_score,
            country_encoded,
            gender_encoded,
            age,
            tenure,
            balance,
            num_products,
            has_card,
            is_active,
            salary
        ]])

        # Scale if needed
        features = scaler.transform(features)

        # Predict
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] 

        result = int(prediction)
        proba = round(probability * 100, 2)

                # -----------------------------
        # 🔥 AI Retention Suggestions
        # -----------------------------

        

        if credit_score < 450:
            suggestions.append("Assign financial counseling & secured credit card offer")

        if 450 <= credit_score < 600:
            suggestions.append("Offer EMI restructuring or flexible repayment options")

        if age >= 60:
            suggestions.append("Provide senior citizen benefits with higher FD interest")

        if age < 25:
            suggestions.append("Offer student banking benefits and zero-fee services")

        if tenure < 1:
            suggestions.append("Provide welcome retention package and onboarding support")

        if tenure > 8 and probability > 0.6:
            suggestions.append("Escalate to relationship manager immediately")

        if balance > 100000 and probability > 0.5:
            suggestions.append("Offer wealth management consultation")

        if balance < 1000 and is_active == 0:
            suggestions.append("Send account activation incentives")

        if num_products >= 3 and probability > 0.5:
            suggestions.append("Conduct customer satisfaction review call")

        if num_products == 1:
            suggestions.append("Promote bundled financial products")

        if has_card == 0:
            suggestions.append("Offer lifetime free credit card")

        if is_active == 0:
            suggestions.append("Provide cashback on next 5 transactions")

        if salary > 120000:
            suggestions.append("Upgrade to Platinum banking program")

        if salary > 200000 and probability > 0.5:
            suggestions.append("Assign dedicated wealth advisor")

        if probability > 0.75:
            suggestions.append("Immediate retention action required - High churn risk")

        if 0.4 < probability <= 0.75:
            suggestions.append("Send personalized retention offer email")

        if probability <= 0.4:
            suggestions.append("Maintain engagement through loyalty rewards")


        # Save to DB
        ChurnPrediction.objects.update_or_create(
            customer_id=customer_id,
            defaults={
                'credit_score': credit_score,
                'country': country,
                'gender': gender,
                'age': age,
                'tenure': tenure,
                'balance': balance,
                'num_products': num_products,
                'has_card': has_card,
                'is_active': is_active,
                'salary': salary,
                'prediction': result,
                'probability': proba
            }
        )

    return render(request, 'predict.html', {
        'prediction_result': result,
        'prediction_proba': proba,
        "suggestions": suggestions,
        **form_data
    })


@login_required
def dashboard_data(request):

    customers = ChurnPrediction.objects.all()
    total = customers.count()

    high = customers.filter(prediction=1).count()
    low = customers.filter(prediction=0).count()

    retention = round((low / total) * 100, 2) if total > 0 else 0

    # Chart Data
    churn_labels = ["Low Risk", "High Risk"]
    churn_values = [low, high]

    response = {
        "total_customers": total,
        "high_risk": high,
        "retention_rate": retention,
        "low_risk": low,

        "chart_labels": churn_labels,
        "chart_values": churn_values,
    }

    return JsonResponse(response)

@login_required
def edit_customer(request, id):
    customer = ChurnPrediction.objects.get(id=id)

    if request.method == 'POST':
        customer.customer_id = request.POST['customer_id']
        customer.credit_score = request.POST['credit_score']
        customer.country = request.POST['country']
        customer.gender = request.POST['gender']
        customer.age = request.POST['age']
        customer.tenure = request.POST['tenure']
        customer.balance = request.POST['balance']
        customer.salary = request.POST['salary']
        customer.save()

        return redirect('customers')

    return render(request, 'edit_customer.html', {'customer': customer})

@login_required
def delete_customer(request, id):
    customer = ChurnPrediction.objects.get(id=id)
    customer.delete()
    return redirect('customers')

@login_required
def upload_csv(request):
    if request.method == "POST":
        csv_file = request.FILES['file']
        data = csv.reader(TextIOWrapper(csv_file, encoding='utf-8'))
        next(data)  # Skip header row

        for row in data:
            ChurnPrediction.objects.update_or_create(
                customer_id=row[0],
                defaults={
                    'credit_score': int(row[1]),
                    'country': row[2],
                    'gender': row[3],
                    'age': int(row[4]),
                    'tenure': int(row[5]),
                    'balance': float(row[6]),
                    'num_products': int(row[7]),
                    'has_card': int(row[8]),
                    'is_active': int(row[9]),
                    'salary': float(row[10]),
                    'prediction': int(row[11]),
                    'probability': float(row[12])
                }
            )

        return redirect('customers')

    return render(request, 'upload_data.html')