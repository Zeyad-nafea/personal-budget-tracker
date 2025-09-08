import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os


class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("900x650")
        self.root.configure(bg='#f5f5f5')
        
        # Data variables
        self.transactions = []
        self.categories = {}
        self.budget = 0
        self.current_user = None
        self.data_folder = "user_data"
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        # Show login first
        self.show_login()
    
    def get_user_file_path(self, filename):
        """Get the file path for current user's data file"""
        if not self.current_user:
            return filename
        user_folder = os.path.join(self.data_folder, self.current_user)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        return os.path.join(user_folder, filename)
    
    def show_login(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Login frame
        login_frame = tk.Frame(self.root, bg='#34495e', padx=50, pady=50)
        login_frame.pack(expand=True, fill='both')
        
        # Title
        title = tk.Label(login_frame, text="💰 Budget Tracker", 
                        font=('Arial', 28, 'bold'), fg='white', bg='#34495e')
        title.pack(pady=30)
        
        # Login form
        form_frame = tk.Frame(login_frame, bg='white', padx=40, pady=30, relief='ridge', bd=3)
        form_frame.pack()
        
        tk.Label(form_frame, text="Username:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        self.username_entry = tk.Entry(form_frame, font=('Arial', 12), width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_frame, text="Password:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.password_entry = tk.Entry(form_frame, font=('Arial', 12), width=25, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        login_btn = tk.Button(btn_frame, text="Login", command=self.login,
                             bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                             padx=30, pady=8, cursor='hand2')
        login_btn.pack(side='left', padx=10)
        
        register_btn = tk.Button(btn_frame, text="Register", command=self.register,
                               bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                               padx=30, pady=8, cursor='hand2')
        register_btn.pack(side='left', padx=10)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        if self.user_identify(username, password):
            self.current_user = username
            # Load user-specific data after successful login
            self.load_data()
            messagebox.showinfo("Welcome!", f"Hello {username}! 👋")
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Invalid credentials! Please try again.")
    
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        if self.user_identify(username, password):
            messagebox.showerror("Error", "Username already exists!")
            return
        
        with open('user_info.txt', 'a') as file:
            file.write(f'{username},{password}\n')
        messagebox.showinfo("Success", "Account created! You can now login.")
    
    def show_main_app(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"💰 Budget Tracker - {self.current_user}", 
                font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50').pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left side - Controls with scrollbar
        left_outer_frame = tk.Frame(main_container, width=350)
        left_outer_frame.pack(side='left', fill='y', padx=(0, 15))
        left_outer_frame.pack_propagate(False)
        
        # Create canvas and scrollbar for left panel
        canvas = tk.Canvas(left_outer_frame, bg='white', width=330)
        scrollbar = ttk.Scrollbar(left_outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        left_frame = tk.LabelFrame(scrollable_frame, text="Controls", 
                                  font=('Arial', 14, 'bold'), bg='white')
        left_frame.pack(fill='x', padx=5, pady=5)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Right side - Display
        right_frame = tk.LabelFrame(main_container, text="Overview", 
                                   font=('Arial', 14, 'bold'), bg='white')
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.setup_controls(left_frame)
        self.setup_display(right_frame)
        self.update_display()
    
    def setup_controls(self, parent):
        # Budget section
        budget_frame = tk.LabelFrame(parent, text="💳 Budget", font=('Arial', 11, 'bold'), 
                                   bg='white', padx=15, pady=10)
        budget_frame.pack(fill='x', padx=15, pady=10)
        
        self.budget_label = tk.Label(budget_frame, text=f"Current: ${self.budget:.2f}", 
                                    font=('Arial', 11), bg='white')
        self.budget_label.pack(anchor='w', pady=5)
        
        tk.Button(budget_frame, text="Set Budget", command=self.set_budget,
                 bg='#3498db', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(budget_frame, text="Update Budget", command=self.update_budget,
                 bg='#f39c12', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        
        # Categories section
        cat_frame = tk.LabelFrame(parent, text="📂 Categories", font=('Arial', 11, 'bold'), 
                                 bg='white', padx=15, pady=10)
        cat_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Button(cat_frame, text="Add Category", command=self.add_category,
                 bg='#2ecc71', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(cat_frame, text="View Categories", command=self.show_categories,
                 bg='#95a5a6', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(cat_frame, text="Delete Category", command=self.delete_category,
                 bg='#e74c3c', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        
        # Transactions section
        trans_frame = tk.LabelFrame(parent, text="💸 Transactions", font=('Arial', 11, 'bold'), 
                                   bg='white', padx=15, pady=10)
        trans_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Button(trans_frame, text="Add Transaction", command=self.add_transaction,
                 bg='#e67e22', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(trans_frame, text="View All Transactions", command=self.view_transactions,
                 bg='#9b59b6', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(trans_frame, text="Search Transactions", command=self.search_transactions,
                 bg='#1abc9c', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        
        # Savings section
        saving_frame = tk.LabelFrame(parent, text="🎯 Savings", font=('Arial', 11, 'bold'), 
                                    bg='white', padx=15, pady=10)
        saving_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Button(saving_frame, text="Add Saving Goal", command=self.add_saving_goal,
                 bg='#27ae60', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(saving_frame, text="Add to Savings", command=self.add_saving,
                 bg='#16a085', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(saving_frame, text="View Progress", command=self.view_savings_progress,
                 bg='#2ecc71', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        
        # Utils section
        util_frame = tk.LabelFrame(parent, text="⚙️ Tools", font=('Arial', 11, 'bold'), 
                                  bg='white', padx=15, pady=10)
        util_frame.pack(fill='x', padx=15, pady=(10, 0))
        
        tk.Button(util_frame, text="Monthly Report", command=self.monthly_report,
                 bg='#34495e', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(util_frame, text="Export Data", command=self.export_data,
                 bg='#7f8c8d', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(util_frame, text="Clear All Data", command=self.clear_all_data,
                 bg='#c0392b', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
        tk.Button(util_frame, text="Logout", command=self.logout,
                 bg='#8e44ad', fg='white', font=('Arial', 10), cursor='hand2', width=15).pack(pady=2)
    
    def setup_display(self, parent):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Overview tab
        self.overview_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.overview_tab, text='📊 Overview')
        
        # Chart tab
        self.chart_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.chart_tab, text='📈 Charts')
        
        # Recent tab
        self.recent_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.recent_tab, text='🕐 Recent')
    
    def update_display(self):
        # Clear tabs
        for widget in self.overview_tab.winfo_children():
            widget.destroy()
        for widget in self.chart_tab.winfo_children():
            widget.destroy()
        for widget in self.recent_tab.winfo_children():
            widget.destroy()
        
        self.show_overview()
        self.show_charts()
        self.show_recent()
    
    def show_overview(self):
        total_spent = sum(t['amount'] for t in self.transactions)
        remaining = self.budget - total_spent
        avg_spending = total_spent / len(self.transactions) if self.transactions else 0
        
        # Budget status
        status_frame = tk.Frame(self.overview_tab, bg='#ecf0f1', relief='groove', bd=2)
        status_frame.pack(fill='x', padx=20, pady=15)
        
        tk.Label(status_frame, text="Budget Status", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1').pack(pady=10)
        
        info_grid = tk.Frame(status_frame, bg='#ecf0f1')
        info_grid.pack(pady=10)
        
        # Budget info
        tk.Label(info_grid, text=f"💰 Total Budget:", font=('Arial', 12, 'bold'), 
                bg='#ecf0f1').grid(row=0, column=0, sticky='w', padx=20, pady=5)
        tk.Label(info_grid, text=f"${self.budget:.2f}", font=('Arial', 12), 
                bg='#ecf0f1').grid(row=0, column=1, sticky='w', padx=20, pady=5)
        
        tk.Label(info_grid, text=f"💸 Total Spent:", font=('Arial', 12, 'bold'), 
                bg='#ecf0f1').grid(row=1, column=0, sticky='w', padx=20, pady=5)
        tk.Label(info_grid, text=f"${total_spent:.2f}", font=('Arial', 12), 
                bg='#ecf0f1').grid(row=1, column=1, sticky='w', padx=20, pady=5)
        
        # Remaining budget with color
        remaining_color = '#e74c3c' if remaining < 0 else '#27ae60'
        remaining_emoji = '⚠️' if remaining < 0 else '✅'
        tk.Label(info_grid, text=f"{remaining_emoji} Remaining:", font=('Arial', 12, 'bold'), 
                bg='#ecf0f1').grid(row=2, column=0, sticky='w', padx=20, pady=5)
        tk.Label(info_grid, text=f"${remaining:.2f}", font=('Arial', 12, 'bold'), 
                fg=remaining_color, bg='#ecf0f1').grid(row=2, column=1, sticky='w', padx=20, pady=5)
        
        tk.Label(info_grid, text=f"📈 Average per Transaction:", font=('Arial', 12, 'bold'), 
                bg='#ecf0f1').grid(row=3, column=0, sticky='w', padx=20, pady=5)
        tk.Label(info_grid, text=f"${avg_spending:.2f}", font=('Arial', 12), 
                bg='#ecf0f1').grid(row=3, column=1, sticky='w', padx=20, pady=5)
        
        # Quick stats
        stats_frame = tk.Frame(self.overview_tab, bg='#ffffff', relief='groove', bd=2)
        stats_frame.pack(fill='x', padx=20, pady=15)
        
        tk.Label(stats_frame, text="Quick Stats", font=('Arial', 16, 'bold')).pack(pady=10)
        
        stats_info = tk.Frame(stats_frame)
        stats_info.pack()
        
        tk.Label(stats_info, text=f"📝 Total Transactions: {len(self.transactions)}", 
                font=('Arial', 11)).pack(anchor='w', padx=20, pady=3)
        tk.Label(stats_info, text=f"📁 Categories: {len(self.categories)}", 
                font=('Arial', 11)).pack(anchor='w', padx=20, pady=3)
        
        # Update budget label in controls
        if hasattr(self, 'budget_label'):
            self.budget_label.config(text=f"Current: ${self.budget:.2f}")
    
    def show_charts(self):
        if not self.transactions:
            tk.Label(self.chart_tab, text="No data to display 📊\nAdd some transactions first!", 
                    font=('Arial', 14), fg='gray').pack(expand=True)
            return
        
        # Calculate spending by category
        category_totals = {}
        for transaction in self.transactions:
            cat = transaction['category']
            category_totals[cat] = category_totals.get(cat, 0) + transaction['amount']
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        wedges, texts, autotexts = ax.pie(category_totals.values(), 
                                         labels=category_totals.keys(), 
                                         autopct='%1.1f%%',
                                         colors=colors[:len(category_totals)])
        ax.set_title('Spending by Category', fontsize=16, fontweight='bold')
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)
    
    def show_recent(self):
        if not self.transactions:
            tk.Label(self.recent_tab, text="No transactions yet 🕐\nAdd your first transaction!", 
                    font=('Arial', 14), fg='gray').pack(expand=True)
            return
        
        # Recent transactions table
        tk.Label(self.recent_tab, text="Recent Transactions", 
                font=('Arial', 16, 'bold')).pack(pady=15)
        
        # Create treeview
        columns = ('Date', 'Category', 'Amount')
        tree = ttk.Treeview(self.recent_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('Date', text='📅 Date')
        tree.heading('Category', text='📂 Category')
        tree.heading('Amount', text='💵 Amount')
        
        tree.column('Date', width=120)
        tree.column('Category', width=150)
        tree.column('Amount', width=100)
        
        # Add transactions (newest first)
        for transaction in reversed(self.transactions[-20:]):  # Show last 20
            date = transaction.get('date', 'N/A')
            tree.insert('', 'end', values=(
                date,
                transaction['category'],
                f"${transaction['amount']:.2f}"
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.recent_tab, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side='right', fill='y', padx=(0, 15), pady=15)
    
    # Core functions (keeping your original logic)
    def set_budget(self):
        budget = simpledialog.askfloat("Set Budget", "Enter budget amount:")
        if budget is not None and budget >= 0:
            self.budget = budget
            with open(self.get_user_file_path("budget.txt"), "w") as file:
                file.write(str(budget))
            self.update_display()
            messagebox.showinfo("Success", f"Budget set to ${budget:.2f}")
        elif budget is not None:
            messagebox.showerror("Error", "Budget cannot be negative!")
    
    def update_budget(self):
        new_budget = simpledialog.askfloat("Update Budget", 
                                          f"Current budget: ${self.budget:.2f}\nEnter new amount:")
        if new_budget is not None and new_budget >= 0:
            self.budget = new_budget
            with open(self.get_user_file_path("budget.txt"), "w") as file:
                file.write(str(new_budget))
            self.update_display()
            messagebox.showinfo("Success", f"Budget updated to ${new_budget:.2f}")
        elif new_budget is not None:
            messagebox.showerror("Error", "Budget cannot be negative!")
    
    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter category name:")
        if not category or not category.strip():
            return
        
        category = category.strip()
        
        # Check if category exists
        try:
            with open(self.get_user_file_path("categories.txt"), "r") as file:
                existing = {line.strip() for line in file}
        except FileNotFoundError:
            existing = set()
        
        if category in existing:
            messagebox.showwarning("Warning", "Category already exists!")
            return
        
        self.categories[category] = []
        with open(self.get_user_file_path("categories.txt"), "a") as file:
            file.write(f"{category}\n")
        messagebox.showinfo("Success", f"Category '{category}' added!")
    
    def show_categories(self):
        if not self.categories:
            messagebox.showinfo("Categories", "No categories available.")
            return
        
        categories_text = "Available Categories:\n\n"
        for cat in self.categories.keys():
            categories_text += f"• {cat}\n"
        messagebox.showinfo("Categories", categories_text)
    
    def delete_category(self):
        if not self.categories:
            messagebox.showinfo("Delete Category", "No categories to delete.")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Category")
        dialog.geometry("300x200")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="Select category to delete:", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
        
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, 
                                     values=list(self.categories.keys()), width=25)
        category_combo.pack(pady=10)
        
        def confirm_delete():
            category = category_var.get()
            if not category:
                messagebox.showerror("Error", "Please select a category!")
                return
            
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Delete category '{category}'?\nThis will remove all transactions in this category!")
            if result:
                # Remove from memory
                if category in self.categories:
                    del self.categories[category]
                
                # Remove transactions of this category
                self.transactions = [t for t in self.transactions if t['category'] != category]
                
                # Update files
                self.save_data()
                self.update_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"Category '{category}' deleted!")
        
        tk.Button(dialog, text="Delete", command=confirm_delete,
                 bg='#e74c3c', fg='white', font=('Arial', 10), 
                 padx=20, pady=5, cursor='hand2').pack(pady=20)
    
    def add_transaction(self):
        if not self.categories:
            messagebox.showwarning("Warning", "Please add at least one category first!")
            return
        
        # Transaction dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Transaction")
        dialog.geometry("350x300")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="💸 Add New Transaction", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=15)
        
        # Amount input
        tk.Label(dialog, text="Amount:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=30)
        amount_entry = tk.Entry(dialog, font=('Arial', 12), width=25)
        amount_entry.pack(padx=30, pady=5)
        
        # Category selection
        tk.Label(dialog, text="Category:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=30, pady=(10,0))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, 
                                     values=list(self.categories.keys()), width=23)
        category_combo.pack(padx=30, pady=5)
        
        # Description input (new feature)
        tk.Label(dialog, text="Description (optional):", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', padx=30, pady=(10,0))
        desc_entry = tk.Entry(dialog, font=('Arial', 12), width=25)
        desc_entry.pack(padx=30, pady=5)
        
        def add_transaction_action():
            try:
                amount = float(amount_entry.get())
                category = category_var.get()
                description = desc_entry.get().strip()
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be positive!")
                    return
                
                if not category:
                    messagebox.showerror("Error", "Please select a category!")
                    return
                
                # Create transaction
                transaction = {
                    'amount': amount,
                    'category': category,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'description': description if description else 'No description'
                }
                
                self.transactions.append(transaction)
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(amount)
                
                # Save to file (keeping your original format)
                with open(self.get_user_file_path("transactions.txt"), "a") as file:
                    file.write(f"{category},{amount},{transaction['date']},{description}\n")
                
                self.update_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"${amount:.2f} added to {category}!")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount!")
        
        tk.Button(dialog, text="Add Transaction", command=add_transaction_action,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'), 
                 padx=30, pady=8, cursor='hand2').pack(pady=20)
        
        # Focus on amount entry
        amount_entry.focus()
    
    def view_transactions(self):
        if not self.transactions:
            messagebox.showinfo("Transactions", "No transactions found.")
            return
        
        # Create transactions window
        trans_window = tk.Toplevel(self.root)
        trans_window.title("All Transactions")
        trans_window.geometry("700x500")
        
        tk.Label(trans_window, text="All Transactions", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Create treeview with scrollbar
        tree_frame = tk.Frame(trans_window)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        columns = ('Date', 'Category', 'Amount', 'Description')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
        tree.column('Date', width=100)
        tree.column('Category', width=150)
        tree.column('Amount', width=100)
        tree.column('Description', width=200)
        
        # Add all transactions
        for transaction in reversed(self.transactions):  # Newest first
            tree.insert('', 'end', values=(
                transaction.get('date', 'N/A'),
                transaction['category'],
                f"${transaction['amount']:.2f}",
                transaction.get('description', 'No description')
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def search_transactions(self):
        if not self.transactions:
            messagebox.showinfo("Search", "No transactions to search.")
            return
        
        search_term = simpledialog.askstring("Search Transactions", 
                                           "Enter category or description to search:")
        if not search_term:
            return
        
        search_term = search_term.lower()
        results = []
        
        for transaction in self.transactions:
            if (search_term in transaction['category'].lower() or 
                search_term in transaction.get('description', '').lower()):
                results.append(transaction)
        
        if not results:
            messagebox.showinfo("Search Results", f"No transactions found for '{search_term}'")
            return
        
        # Show results window
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Search Results for '{search_term}'")
        result_window.geometry("600x400")
        
        tk.Label(result_window, text=f"Found {len(results)} transactions", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Results table
        columns = ('Date', 'Category', 'Amount', 'Description')
        tree = ttk.Treeview(result_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
        
        for transaction in results:
            tree.insert('', 'end', values=(
                transaction.get('date', 'N/A'),
                transaction['category'],
                f"${transaction['amount']:.2f}",
                transaction.get('description', 'No description')
            ))
        
        tree.pack(fill='both', expand=True, padx=15, pady=15)
    
    def add_saving_goal(self):
        category = simpledialog.askstring("Saving Goal", "Enter saving category:")
        if not category or not category.strip():
            return
        
        goal = simpledialog.askfloat("Saving Goal", f"Enter saving goal for {category}:")
        if goal is not None and goal > 0:
            with open(self.get_user_file_path('saving_target.txt'), 'a') as file:
                file.write(f"{category},{goal}\n")
            messagebox.showinfo("Success", f"Saving goal of ${goal:.2f} set for {category}!")
        elif goal is not None:
            messagebox.showerror("Error", "Goal amount must be positive!")
    
    def add_saving(self):
        category = simpledialog.askstring("Add Saving", "Enter saving category:")
        if not category or not category.strip():
            return
        
        amount = simpledialog.askfloat("Add Saving", f"Enter amount to save for {category}:")
        if amount is not None and amount > 0:
            with open(self.get_user_file_path('saving_data.txt'), 'a') as file:
                file.write(f"{category},{amount}\n")
            messagebox.showinfo("Success", f"${amount:.2f} added to {category} savings!")
        elif amount is not None:
            messagebox.showerror("Error", "Amount must be positive!")
    
    def view_savings_progress(self):
        try:
            progress = self.saving_progress()
            if not progress:
                messagebox.showinfo("Savings Progress", "No saving goals found.")
                return
            
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Savings Progress")
            progress_window.geometry("400x300")
            progress_window.configure(bg='white')
            
            tk.Label(progress_window, text="🎯 Savings Progress", 
                    font=('Arial', 16, 'bold')).pack(pady=15)
            
            progress_frame = tk.Frame(progress_window, bg='white')
            progress_frame.pack(fill='both', expand=True, padx=20)
            
            for category, percentage in progress.items():
                cat_frame = tk.Frame(progress_frame, bg='#ecf0f1', relief='ridge', bd=1)
                cat_frame.pack(fill='x', pady=5)
                
                tk.Label(cat_frame, text=category, font=('Arial', 12, 'bold'), 
                        bg='#ecf0f1').pack(anchor='w', padx=10, pady=5)
                
                # Progress bar
                progress_bar = ttk.Progressbar(cat_frame, length=250, mode='determinate')
                progress_bar['value'] = min(percentage, 100)
                progress_bar.pack(padx=10, pady=5)
                
                status = "🎉 Goal Achieved!" if percentage >= 100 else f"{percentage:.1f}% Complete"
                tk.Label(cat_frame, text=status, font=('Arial', 10), 
                        bg='#ecf0f1').pack(anchor='w', padx=10, pady=(0, 5))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading savings data: {str(e)}")
    
    def monthly_report(self):
        if not self.transactions:
            messagebox.showinfo("Monthly Report", "No transactions to analyze.")
            return
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Monthly Report")
        report_window.geometry("500x600")
        report_window.configure(bg='white')
        
        # Title
        tk.Label(report_window, text="📊 Monthly Report", 
                font=('Arial', 18, 'bold')).pack(pady=15)
        
        # Scrollable text area
        text_frame = tk.Frame(report_window)
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        text_widget = tk.Text(text_frame, font=('Arial', 11), wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Generate report
        total_spent = sum(t['amount'] for t in self.transactions)
        avg_spending = total_spent / len(self.transactions)
        remaining = self.budget - total_spent
        
        # Category breakdown
        category_totals = {}
        for transaction in self.transactions:
            cat = transaction['category']
            category_totals[cat] = category_totals.get(cat, 0) + transaction['amount']
        
        # Highest and lowest
        highest_cat, highest_amt, lowest_cat, lowest_amt = self.find_highest_and_lowest_spending()
        
        report_text = f"""BUDGET SUMMARY
{'='*40}
Total Budget: ${self.budget:.2f}
Total Spent: ${total_spent:.2f}
Remaining: ${remaining:.2f}
Average per Transaction: ${avg_spending:.2f}

SPENDING ANALYSIS
{'='*40}
Total Transactions: {len(self.transactions)}
"""
        
        if highest_cat:
            report_text += f"Highest Transaction: ${highest_amt:.2f} ({highest_cat})\n"
            report_text += f"Lowest Transaction: ${lowest_amt:.2f} ({lowest_cat})\n"
        
        report_text += f"\nCATEGORY BREAKDOWN\n{'='*40}\n"
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spent) * 100 if total_spent > 0 else 0
            report_text += f"{category}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        text_widget.insert('1.0', report_text)
        text_widget.config(state='disabled')  # Make read-only
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def export_data(self):
        try:
            export_data = {
                'user': self.current_user,
                'budget': self.budget,
                'transactions': self.transactions,
                'categories': list(self.categories.keys()),
                'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            filename = f"budget_export_{self.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as file:
                json.dump(export_data, file, indent=2)
            
            messagebox.showinfo("Export Complete", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def clear_all_data(self):
        result = messagebox.askyesno("Clear All Data", 
                                   "⚠️ Are you sure?\nThis will delete ALL your financial data!")
        if not result:
            return
        
        # Confirm again
        confirm = messagebox.askyesno("Final Confirmation", 
                                    "This action cannot be undone!\nProceed with clearing all data?")
        if confirm:
            self.transactions.clear()
            self.categories.clear()
            self.budget = 0
            
            # Clear files
            files = ["transactions.txt", "saving_data.txt", "saving_target.txt", "budget.txt", "categories.txt"]
            for filename in files:
                try:
                    with open(self.get_user_file_path(filename), 'w') as f:
                        pass  # Clear file
                except:
                    pass
            
            self.update_display()
            messagebox.showinfo("Complete", "All data has been cleared!")
    
    def logout(self):
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            # Clear current user data from memory
            self.current_user = None
            self.transactions.clear()
            self.categories.clear()
            self.budget = 0
            self.show_login()
    
    # Data handling methods (updated for user-specific files)
    def load_data(self):
        # Load budget
        try:
            with open(self.get_user_file_path("budget.txt"), "r") as file:
                budget_str = file.read().strip()
                self.budget = float(budget_str) if budget_str else 0
        except FileNotFoundError:
            self.budget = 0
        
        # Load transactions (enhanced to handle descriptions)
        self.transactions.clear()
        try:
            with open(self.get_user_file_path("transactions.txt"), "r") as file:
                for line in file:
                    if line.strip():
                        parts = line.strip().split(",")
                        if len(parts) >= 2:
                            category = parts[0]
                            amount = float(parts[1])
                            date = parts[2] if len(parts) > 2 else datetime.now().strftime("%Y-%m-%d")
                            description = parts[3] if len(parts) > 3 else "No description"
                            
                            self.transactions.append({
                                "amount": amount,
                                "category": category,
                                "date": date,
                                "description": description
                            })
        except FileNotFoundError:
            pass
        
        # Load categories
        self.categories.clear()
        try:
            with open(self.get_user_file_path("categories.txt"), "r") as file:
                for line in file:
                    category = line.strip()
                    if category:
                        self.categories[category] = []
        except FileNotFoundError:
            pass
    
    def save_data(self):
        # Save budget
        with open(self.get_user_file_path("budget.txt"), "w") as file:
            file.write(str(self.budget))
        
        # Save transactions
        with open(self.get_user_file_path("transactions.txt"), "w") as file:
            for transaction in self.transactions:
                date = transaction.get('date', datetime.now().strftime("%Y-%m-%d"))
                desc = transaction.get('description', 'No description')
                file.write(f"{transaction['category']},{transaction['amount']},{date},{desc}\n")
        
        # Save categories
        with open(self.get_user_file_path("categories.txt"), "w") as file:
            for category in self.categories:
                file.write(f"{category}\n")
    
    # Original functions adapted
    def user_identify(self, username, password):
        try:
            with open('user_info.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2 and username == parts[0] and password == parts[1]:
                        return True
        except FileNotFoundError:
            pass
        return False
    
    def saving_progress(self):
        saving_dict = {}
        saving_target_dict = {}
        
        try:
            with open(self.get_user_file_path('saving_data.txt'), 'r') as file:
                for line in file:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            category, amount = parts[0], float(parts[1])
                            saving_dict[category] = saving_dict.get(category, 0) + amount
        except FileNotFoundError:
            pass
        
        try:
            with open(self.get_user_file_path('saving_target.txt'), 'r') as file:
                for line in file:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            category, target = parts[0], float(parts[1])
                            saving_target_dict[category] = target
        except FileNotFoundError:
            pass
        
        progress = {}
        for category, target in saving_target_dict.items():
            saved = saving_dict.get(category, 0)
            progress[category] = (saved / target) * 100 if target > 0 else 0
        
        return progress
    
    def find_highest_and_lowest_spending(self):
        if not self.transactions:
            return None, None, None, None
        
        amounts = [t['amount'] for t in self.transactions]
        categories = [t['category'] for t in self.transactions]
        
        highest_amount = max(amounts)
        lowest_amount = min(amounts)
        highest_category = categories[amounts.index(highest_amount)]
        lowest_category = categories[amounts.index(lowest_amount)]
        
        return highest_category, highest_amount, lowest_category, lowest_amount

def main():
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()