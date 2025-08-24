import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog, colorchooser
import csv, os
from collections import Counter
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

CSV_FILE = 'bmi_results.csv'


languages = {
    "fa": {
        "title": "محاسبه BMI حرفه‌ای",
        "name": "نام:",
        "age": "سن:",
        "gender": "جنسیت:",
        "weight": "وزن (کیلوگرم):",
        "height": "قد (متر):",
        "calc_btn": "محاسبه BMI",
        "chart_btn": "نمایش نمودار وضعیت BMI",
        "pdf_btn": "تولید گزارش PDF",
        "bg_btn": "انتخاب رنگ پس‌زمینه",
        "font_btn": "انتخاب فونت",
        "status_under": "کم‌وزن",
        "status_normal": "نرمال",
        "status_over": "اضافه وزن",
        "status_obese": "چاق",
        "advice_under": "رژیم پروتئینی و تمرین با وزنه",
        "advice_normal": "حفظ وزن با ورزش منظم",
        "advice_over": "رژیم کم کالری و ورزش هوازی",
        "advice_obese": "مشاوره پزشکی و برنامه ورزشی حرفه‌ای",
        "error_empty": "لطفاً همه اطلاعات شخصی را وارد کنید!",
        "error_number": "لطفاً اعداد معتبر برای وزن و قد وارد کنید!",
        "filter_name": "نام کاربر برای فیلتر (خالی برای همه):",
        "filter_status": "وضعیت BMI برای فیلتر (کم‌وزن، نرمال، اضافه وزن، چاق) یا خالی برای همه:"
    },
    "en": {
        "title": "Professional BMI Calculator",
        "name": "Name:",
        "age": "Age:",
        "gender": "Gender:",
        "weight": "Weight (kg):",
        "height": "Height (m):",
        "calc_btn": "Calculate BMI",
        "chart_btn": "Show BMI Status Chart",
        "pdf_btn": "Generate PDF Report",
        "bg_btn": "Choose Background Color",
        "font_btn": "Choose Font",
        "status_under": "Underweight",
        "status_normal": "Normal",
        "status_over": "Overweight",
        "status_obese": "Obese",
        "advice_under": "Protein diet and weight training",
        "advice_normal": "Maintain weight with regular exercise",
        "advice_over": "Low-calorie diet and cardio exercises",
        "advice_obese": "Medical consultation and professional exercise plan",
        "error_empty": "Please fill in all personal information!",
        "error_number": "Please enter valid numbers for weight and height!",
        "filter_name": "User name for filter (leave blank for all):",
        "filter_status": "BMI status for filter (Underweight, Normal, Overweight, Obese) or leave blank:"
    }
}


root_temp = tk.Tk()
root_temp.withdraw()  
lang_choice = simpledialog.askstring("Language / زبان", "Choose language: fa / en")
root_temp.destroy()
if lang_choice not in languages:
    lang_choice = "fa"
lang = languages[lang_choice]


def calculate_bmi():
    try:
        name = entry_name.get().strip()
        age = entry_age.get().strip()
        gender = combo_gender.get()
        weight = float(entry_weight.get())
        height = float(entry_height.get())

        if not name or not age or not gender:
            messagebox.showwarning("Error", lang["error_empty"])
            return

        bmi = weight / (height ** 2)

        if bmi < 18.5:
            status = lang["status_under"]
            advice = lang["advice_under"]
        elif 18.5 <= bmi < 24.9:
            status = lang["status_normal"]
            advice = lang["advice_normal"]
        elif 25 <= bmi < 29.9:
            status = lang["status_over"]
            advice = lang["advice_over"]
        else:
            status = lang["status_obese"]
            advice = lang["advice_obese"]

        result_text = (
            f"{lang['name']} {name}\n{lang['age']} {age}\n{lang['gender']} {gender}\n"
            f"BMI: {bmi:.2f}\n{status}\n{advice}"
        )
        messagebox.showinfo("Result", result_text)

        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([lang['name'], lang['age'], lang['gender'], lang['weight'], lang['height'],
                                 "BMI", "Status", "Advice"])
            writer.writerow([name, age, gender, weight, height, round(bmi,2), status, advice])

        entry_weight.delete(0, tk.END)
        entry_height.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Error", lang["error_number"])

def filter_data(name_filter=None, status_filter=None):
    if not os.path.isfile(CSV_FILE):
        messagebox.showwarning("Error", "CSV file does not exist!")
        return []
    filtered = []
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if name_filter and name_filter.lower() not in row[lang['name']].lower():
                continue
            if status_filter and status_filter != row['Status']:
                continue
            filtered.append(row)
    return filtered

def show_bmi_chart():
    name_filter = simpledialog.askstring("Filter", lang["filter_name"])
    status_filter = simpledialog.askstring("Filter", lang["filter_status"])
    data = filter_data(name_filter, status_filter)
    if not data:
        messagebox.showinfo("Result", "No data to display!")
        return

    statuses = [row['Status'] for row in data]
    counts = Counter(statuses)
    categories = [lang["status_under"], lang["status_normal"], lang["status_over"], lang["status_obese"]]
    values = [counts.get(cat,0) for cat in categories]

    plt.bar(categories, values, color=["#87CEFA","#32CD32","#FFA500","#FF4500"])
    plt.title("BMI Status Distribution")
    plt.ylabel("Number of Users")
    plt.show()

def generate_bmi_report():
    name_filter = simpledialog.askstring("Filter", lang["filter_name"])
    status_filter = simpledialog.askstring("Filter", lang["filter_status"])
    data = filter_data(name_filter, status_filter)
    if not data:
        messagebox.showinfo("Result", "No data to generate report!")
        return

    counts = Counter([row['Status'] for row in data])
    categories = [lang["status_under"], lang["status_normal"], lang["status_over"], lang["status_obese"]]
    values = [counts.get(cat,0) for cat in categories]

    plt.bar(categories, values, color=["#87CEFA","#32CD32","#FFA500","#FF4500"])
    chart_file = "bmi_chart.png"
    plt.savefig(chart_file)
    plt.close()

    pdf_file = "BMI_Report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, lang["title"])
    c.setFont("Helvetica", 12)
    c.drawString(50, height-70, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 100
    c.drawString(50, y, f"{lang['name']}  {lang['age']}  {lang['gender']}  {lang['weight']}  {lang['height']}  BMI  Status  Advice")
    y -= 20
    for row in data:
        line = f"{row[lang['name']]}  {row[lang['age']]}  {row[lang['gender']]}  {row[lang['weight']]}  {row[lang['height']]}  {row['BMI']}  {row['Status']}  {row['Advice']}"
        c.drawString(50, y, line)
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    c.showPage()
    c.drawImage(chart_file, 50, height/2-100, width=500, height=300)
    c.save()
    messagebox.showinfo("Success", f"PDF report created successfully: {pdf_file}")

def choose_bg_color():
    color = colorchooser.askcolor()[1]
    if color:
        root.configure(bg=color)
        for tab in notebook.winfo_children():
            tab.configure(bg=color)

def choose_font():
    f = simpledialog.askstring("Font", "Enter font family (e.g., Arial, Times New Roman):")
    if f:
        global my_font
        my_font.config(family=f)


root = tk.Tk()
root.title(lang["title"])
root.geometry("600x400")
root.configure(bg="#f0f8ff")
my_font = font.Font(family="Arial", size=12, weight="bold")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# تب 1: محاسبه BMI
tab1 = tk.Frame(notebook, bg="#f0f8ff")
notebook.add(tab1, text=lang["calc_btn"])

label_name = tk.Label(tab1, text=lang["name"], bg="#f0f8ff", font=my_font)
label_name.grid(row=0, column=0, padx=10, pady=10)
entry_name = tk.Entry(tab1, font=my_font)
entry_name.grid(row=0, column=1, padx=10, pady=10)

label_age = tk.Label(tab1, text=lang["age"], bg="#f0f8ff", font=my_font)
label_age.grid(row=1, column=0, padx=10, pady=10)
entry_age = tk.Entry(tab1, font=my_font)
entry_age.grid(row=1, column=1, padx=10, pady=10)

label_gender = tk.Label(tab1, text=lang["gender"], bg="#f0f8ff", font=my_font)
label_gender.grid(row=2, column=0, padx=10, pady=10)
combo_gender = ttk.Combobox(tab1, values=["Male","Female"] if lang_choice=="en" else ["مرد","زن"], font=my_font)
combo_gender.grid(row=2, column=1, padx=10, pady=10)

label_weight = tk.Label(tab1, text=lang["weight"], bg="#f0f8ff", font=my_font)
label_weight.grid(row=3, column=0, padx=10, pady=10)
entry_weight = tk.Entry(tab1, font=my_font)
entry_weight.grid(row=3, column=1, padx=10, pady=10)

label_height = tk.Label(tab1, text=lang["height"], bg="#f0f8ff", font=my_font)
label_height.grid(row=4, column=0, padx=10, pady=10)
entry_height = tk.Entry(tab1, font=my_font)
entry_height.grid(row=4, column=1, padx=10, pady=10)

btn_calc = tk.Button(tab1, text=lang["calc_btn"], command=calculate_bmi,
                     bg="#00bfff", fg="white", font=my_font)
btn_calc.grid(row=5, column=0, columnspan=2, pady=20)

# تب 2: نمودار BMI
tab2 = tk.Frame(notebook, bg="#f0f8ff")
notebook.add(tab2, text=lang["chart_btn"])
btn_chart = tk.Button(tab2, text=lang["chart_btn"], command=show_bmi_chart,
                      bg="#32CD32", fg="white", font=my_font)
btn_chart.pack(pady=50)

# تب 3: PDF
tab3 = tk.Frame(notebook, bg="#f0f8ff")
notebook.add(tab3, text=lang["pdf_btn"])
btn_pdf = tk.Button(tab3, text=lang["pdf_btn"], command=generate_bmi_report,
                    bg="#FF6347", fg="white", font=my_font)
btn_pdf.pack(pady=50)


tab4 = tk.Frame(notebook, bg="#f0f8ff")
notebook.add(tab4, text="Settings / تنظیمات")
btn_bg = tk.Button(tab4, text=lang["bg_btn"], command=choose_bg_color, font=my_font)
btn_bg.pack(pady=20)
btn_font = tk.Button(tab4, text=lang["font_btn"], command=choose_font, font=my_font)
btn_font.pack(pady=20)

root.mainloop()
