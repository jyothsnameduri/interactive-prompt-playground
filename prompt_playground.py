import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the OpenAI API wrapper
from openai_wrapper import OpenAIWrapper

class PromptPlayground(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("AI Prompt Playground")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set up styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f8f9fa")
        self.style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"))
        
        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        self.header_label = ttk.Label(self.main_frame, text="AI Prompt Playground", style="Header.TLabel")
        self.header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create left frame (configuration)
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Create right frame (results)
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Set up configuration frame
        self.setup_config_frame()
        
        # Set up results frame
        self.setup_results_frame()
        
        # Batch results data
        self.batch_results = []

    def setup_config_frame(self):
        # Configuration header
        config_header = ttk.Label(self.left_frame, text="Configuration", style="Subheader.TLabel")
        config_header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Model selection
        ttk.Label(self.left_frame, text="Model:").grid(row=1, column=0, sticky="w", pady=5)
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        model_combo = ttk.Combobox(self.left_frame, textvariable=self.model_var, state="readonly")
        model_combo["values"] = ("gpt-3.5-turbo", "gpt-4")
        model_combo.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Product input
        ttk.Label(self.left_frame, text="Product:").grid(row=2, column=0, sticky="w", pady=5)
        self.product_var = tk.StringVar()
        product_entry = ttk.Entry(self.left_frame, textvariable=self.product_var)
        product_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # System prompt
        ttk.Label(self.left_frame, text="System Prompt:").grid(row=3, column=0, sticky="w", pady=5)
        self.system_prompt = scrolledtext.ScrolledText(self.left_frame, height=4)
        self.system_prompt.grid(row=3, column=1, sticky="ew", pady=5)
        self.system_prompt.insert(tk.END, "You are a helpful and knowledgeable Clinical Assistant. Provide clear, accurate medical information, help interpret symptoms, and suggest next steps. Always remind users to consult a licensed doctor for diagnosis or treatment.")
        
        # User prompt
        ttk.Label(self.left_frame, text="User Prompt:").grid(row=4, column=0, sticky="w", pady=5)
        self.user_prompt = scrolledtext.ScrolledText(self.left_frame, height=4)
        self.user_prompt.grid(row=4, column=1, sticky="ew", pady=5)
        self.user_prompt.insert(tk.END, "Write a compelling product description for the following product:")
        
        # Parameters header
        params_header = ttk.Label(self.left_frame, text="Parameters", style="Subheader.TLabel")
        params_header.grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 10))
        
        # Temperature
        ttk.Label(self.left_frame, text="Temperature:").grid(row=6, column=0, sticky="w", pady=5)
        self.temp_frame = ttk.Frame(self.left_frame)
        self.temp_frame.grid(row=6, column=1, sticky="ew", pady=5)
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_label = ttk.Label(self.temp_frame, text="0.7")
        self.temp_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.temp_scale = ttk.Scale(self.temp_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                    variable=self.temp_var, command=self.update_temp_label)
        self.temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Max tokens
        ttk.Label(self.left_frame, text="Max Tokens:").grid(row=7, column=0, sticky="w", pady=5)
        self.tokens_frame = ttk.Frame(self.left_frame)
        self.tokens_frame.grid(row=7, column=1, sticky="ew", pady=5)
        self.tokens_var = tk.IntVar(value=150)
        self.tokens_label = ttk.Label(self.tokens_frame, text="150")
        self.tokens_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.tokens_scale = ttk.Scale(self.tokens_frame, from_=1, to=1000, orient=tk.HORIZONTAL, 
                                     variable=self.tokens_var, command=self.update_tokens_label)
        self.tokens_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Presence penalty
        ttk.Label(self.left_frame, text="Presence Penalty:").grid(row=8, column=0, sticky="w", pady=5)
        self.presence_frame = ttk.Frame(self.left_frame)
        self.presence_frame.grid(row=8, column=1, sticky="ew", pady=5)
        self.presence_var = tk.DoubleVar(value=0.0)
        self.presence_label = ttk.Label(self.presence_frame, text="0.0")
        self.presence_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.presence_scale = ttk.Scale(self.presence_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                       variable=self.presence_var, command=self.update_presence_label)
        self.presence_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frequency penalty
        ttk.Label(self.left_frame, text="Frequency Penalty:").grid(row=9, column=0, sticky="w", pady=5)
        self.frequency_frame = ttk.Frame(self.left_frame)
        self.frequency_frame.grid(row=9, column=1, sticky="ew", pady=5)
        self.frequency_var = tk.DoubleVar(value=0.0)
        self.frequency_label = ttk.Label(self.frequency_frame, text="0.0")
        self.frequency_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.frequency_scale = ttk.Scale(self.frequency_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                        variable=self.frequency_var, command=self.update_frequency_label)
        self.frequency_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Stop sequence
        ttk.Label(self.left_frame, text="Stop Sequence:").grid(row=10, column=0, sticky="w", pady=5)
        self.stop_var = tk.StringVar()
        stop_entry = ttk.Entry(self.left_frame, textvariable=self.stop_var)
        stop_entry.grid(row=10, column=1, sticky="ew", pady=5)
        
        # Buttons
        self.buttons_frame = ttk.Frame(self.left_frame)
        self.buttons_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        self.generate_btn = ttk.Button(self.buttons_frame, text="Generate", command=self.generate_single)
        self.generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.batch_btn = ttk.Button(self.buttons_frame, text="Batch Generate", command=self.generate_batch)
        self.batch_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Configure grid weights for left frame
        self.left_frame.columnconfigure(1, weight=1)

    def setup_results_frame(self):
        # Single result header
        result_header = ttk.Label(self.right_frame, text="Result", style="Subheader.TLabel")
        result_header.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Single result text area
        self.result_frame = ttk.LabelFrame(self.right_frame, text="Output")
        self.result_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.insert(tk.END, "Your generated text will appear here...")
        
        # Parameter summary
        self.param_summary = ttk.Label(self.right_frame, text="")
        self.param_summary.grid(row=2, column=0, sticky="w", pady=(0, 20))
        
        # Batch results header
        batch_header = ttk.Label(self.right_frame, text="Batch Results", style="Subheader.TLabel")
        batch_header.grid(row=3, column=0, sticky="w", pady=(0, 10))
        
        # Batch results table
        self.batch_frame = ttk.Frame(self.right_frame)
        self.batch_frame.grid(row=4, column=0, sticky="nsew")
        
        # Create Treeview for results
        self.tree_columns = ("temp", "tokens", "presence", "frequency", "output")
        self.results_tree = ttk.Treeview(self.batch_frame, columns=self.tree_columns, show="headings", height=10)
        
        # Define headings
        self.results_tree.heading("temp", text="Temperature")
        self.results_tree.heading("tokens", text="Max Tokens")
        self.results_tree.heading("presence", text="Presence Penalty")
        self.results_tree.heading("frequency", text="Frequency Penalty")
        self.results_tree.heading("output", text="Output")
        
        # Define columns
        self.results_tree.column("temp", width=100, anchor=tk.CENTER)
        self.results_tree.column("tokens", width=100, anchor=tk.CENTER)
        self.results_tree.column("presence", width=100, anchor=tk.CENTER)
        self.results_tree.column("frequency", width=100, anchor=tk.CENTER)
        self.results_tree.column("output", width=400)
        
        # Configure row height for better readability
        style = ttk.Style()
        style.configure('Treeview', rowheight=60)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(self.batch_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack tree and scrollbar
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event to view full output
        self.results_tree.bind("<Double-1>", self.view_full_output)
        
        # Reflection section
        reflection_header = ttk.Label(self.right_frame, text="Reflection", style="Subheader.TLabel")
        reflection_header.grid(row=5, column=0, sticky="w", pady=(20, 10))
        
        self.reflection_text = scrolledtext.ScrolledText(self.right_frame, height=5, wrap=tk.WORD)
        self.reflection_text.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        self.reflection_text.insert(tk.END, "Write your reflection on the results here...")
        
        self.save_btn = ttk.Button(self.right_frame, text="Save Reflection", command=self.save_reflection)
        self.save_btn.grid(row=7, column=0, sticky="e")
        
        # Configure grid weights for right frame
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.rowconfigure(4, weight=2)
        self.right_frame.columnconfigure(0, weight=1)

    def update_temp_label(self, value):
        self.temp_label.config(text=f"{float(value):.1f}")
        
    def update_tokens_label(self, value):
        self.tokens_label.config(text=str(int(float(value))))
        
    def update_presence_label(self, value):
        self.presence_label.config(text=f"{float(value):.1f}")
        
    def update_frequency_label(self, value):
        self.frequency_label.config(text=f"{float(value):.1f}")
        
    def generate_single(self):
        # Validate inputs
        if not self.product_var.get():
            messagebox.showerror("Error", "Please enter a product")
            return
            
        if not self.user_prompt.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter a user prompt")
            return
            
        # Disable button during generation
        self.generate_btn.config(state="disabled")
        self.generate_btn["text"] = "Generating..."
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Generating...")
        self.update_idletasks()
        
        # Start generation in a separate thread
        threading.Thread(target=self._generate_single_thread, daemon=True).start()
        
    def _generate_single_thread(self):
        try:
            # Get parameters
            model = self.model_var.get()
            system_prompt = self.system_prompt.get("1.0", tk.END).strip()
            user_prompt = self.user_prompt.get("1.0", tk.END).strip()
            product = self.product_var.get()
            temperature = self.temp_var.get()
            max_tokens = self.tokens_var.get()
            presence_penalty = self.presence_var.get()
            frequency_penalty = self.frequency_var.get()
            stop_sequence = self.stop_var.get() if self.stop_var.get() else None
            
            # Create OpenAI wrapper instance
            openai_api = OpenAIWrapper()
            
            # Generate response
            response_content, error = openai_api.generate_response(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                product=product,
                temperature=temperature,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stop_sequence=stop_sequence
            )
            
            if error:
                raise Exception(error)
            
            # Update UI with result
            self.after(0, self._update_single_result, response_content, {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty
            })
            
        except Exception as e:
            self.after(0, self._update_single_error, str(e))
            
    def _update_single_result(self, content, params):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, content)
        
        # Update parameter summary
        summary = f"Model: {params['model']}, Temperature: {params['temperature']:.1f}, Max Tokens: {params['max_tokens']}, "
        summary += f"Presence Penalty: {params['presence_penalty']:.1f}, Frequency Penalty: {params['frequency_penalty']:.1f}"
        self.param_summary.config(text=summary)
        
        # Reset button
        self.generate_btn.config(state="normal")
        self.generate_btn["text"] = "Generate"
        
    def _update_single_error(self, error_msg):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Error: {error_msg}")
        
        # Reset button
        self.generate_btn.config(state="normal")
        self.generate_btn["text"] = "Generate"
        
    def generate_batch(self):
        # Validate inputs
        if not self.product_var.get():
            messagebox.showerror("Error", "Please enter a product")
            return
            
        if not self.user_prompt.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter a user prompt")
            return
            
        # Confirm batch generation
        if not messagebox.askyesno("Confirm", "This will generate multiple API calls and may take some time. Continue?"):
            return
            
        # Disable button during generation
        self.batch_btn.config(state="disabled")
        self.batch_btn["text"] = "Generating..."
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Generating batch results...")
        self.update_idletasks()
        
        # Start generation in a separate thread
        threading.Thread(target=self._generate_batch_thread, daemon=True).start()
        
    def _generate_batch_thread(self):
        try:
            # Get base parameters
            model = self.model_var.get()
            system_prompt = self.system_prompt.get("1.0", tk.END).strip()
            user_prompt = self.user_prompt.get("1.0", tk.END).strip()
            product = self.product_var.get()
            stop_sequence = self.stop_var.get() if self.stop_var.get() else None
            
            # Parameter variations to test
            temperatures = [0.0, 0.7, 1.2]
            max_tokens_values = [50, 150, 300]
            presence_penalties = [0.0, 1.5]
            frequency_penalties = [0.0, 1.5]
            
            # Store results
            self.batch_results = []
            
            # Create OpenAI wrapper instance
            openai_api = OpenAIWrapper()
            
            # Generate all combinations
            for temp in temperatures:
                for max_tok in max_tokens_values:
                    for pres_pen in presence_penalties:
                        for freq_pen in frequency_penalties:
                            try:
                                # Generate response using the wrapper
                                response_content, error = openai_api.generate_response(
                                    model=model,
                                    system_prompt=system_prompt,
                                    user_prompt=user_prompt,
                                    product=product,
                                    temperature=temp,
                                    max_tokens=max_tok,
                                    presence_penalty=pres_pen,
                                    frequency_penalty=freq_pen,
                                    stop_sequence=stop_sequence
                                )
                                
                                # Store result
                                if error:
                                    result = {
                                        "parameters": {
                                            "temperature": temp,
                                            "max_tokens": max_tok,
                                            "presence_penalty": pres_pen,
                                            "frequency_penalty": freq_pen
                                        },
                                        "error": error
                                    }
                                else:
                                    result = {
                                        "parameters": {
                                            "temperature": temp,
                                            "max_tokens": max_tok,
                                            "presence_penalty": pres_pen,
                                            "frequency_penalty": freq_pen
                                        },
                                        "response": response_content
                                    }
                                
                            except Exception as e:
                                # Store error
                                result = {
                                    "parameters": {
                                        "temperature": temp,
                                        "max_tokens": max_tok,
                                        "presence_penalty": pres_pen,
                                        "frequency_penalty": freq_pen
                                    },
                                    "error": str(e)
                                }
                                
                            self.batch_results.append(result)
                            
                            # Update UI with current result
                            self.after(0, self._add_batch_result, result)
            
            # Update UI when complete
            self.after(0, self._batch_generation_complete)
            
        except Exception as e:
            self.after(0, self._batch_generation_error, str(e))
            
    def _add_batch_result(self, result):
        # Add result to treeview
        params = result["parameters"]
        
        if "error" in result:
            output = f"Error: {result['error']}"
        else:
            output = result["response"]
            
        self.results_tree.insert("", tk.END, values=(
            f"{params['temperature']:.1f}",
            params['max_tokens'],
            f"{params['presence_penalty']:.1f}",
            f"{params['frequency_penalty']:.1f}",
            output
        ))
        
    def _batch_generation_complete(self):
        # Update UI
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Batch generation complete. See results in the table below.")
        
        # Reset button
        self.batch_btn.config(state="normal")
        self.batch_btn["text"] = "Batch Generate"
        
        # Focus on results
        self.results_tree.focus_set()
        
    def _batch_generation_error(self, error_msg):
        # Update UI
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Error in batch generation: {error_msg}")
        
        # Reset button
        self.batch_btn.config(state="normal")
        self.batch_btn["text"] = "Batch Generate"
        
    def view_full_output(self, event):
        """Display the full output text when a row is double-clicked."""
        # Get the selected item
        item = self.results_tree.selection()[0]
        if not item:
            return
            
        # Get the values from the selected item
        values = self.results_tree.item(item, 'values')
        if not values or len(values) < 5:
            return
            
        # Get the output text
        output_text = values[4]
        
        # Create a new window to display the full output
        output_window = tk.Toplevel(self)
        output_window.title("Full Output")
        output_window.geometry("600x400")
        
        # Add parameter information
        params_frame = ttk.Frame(output_window)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text=f"Temperature: {values[0]}").pack(side=tk.LEFT, padx=5)
        ttk.Label(params_frame, text=f"Max Tokens: {values[1]}").pack(side=tk.LEFT, padx=5)
        ttk.Label(params_frame, text=f"Presence Penalty: {values[2]}").pack(side=tk.LEFT, padx=5)
        ttk.Label(params_frame, text=f"Frequency Penalty: {values[3]}").pack(side=tk.LEFT, padx=5)
        
        # Add text area for output
        output_text_area = scrolledtext.ScrolledText(output_window, wrap=tk.WORD)
        output_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        output_text_area.insert(tk.END, output_text)
        output_text_area.config(state=tk.DISABLED)  # Make it read-only
        
        # Add close button
        ttk.Button(output_window, text="Close", command=output_window.destroy).pack(pady=10)
    
    def save_reflection(self):
        reflection = self.reflection_text.get("1.0", tk.END).strip()
        
        if not reflection or reflection == "Write your reflection on the results here...":
            messagebox.showerror("Error", "Please enter your reflection")
            return
            
        # Here you could save the reflection to a file
        try:
            with open("reflection.txt", "w") as f:
                f.write(reflection)
            messagebox.showinfo("Success", "Reflection saved to reflection.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save reflection: {str(e)}")

if __name__ == "__main__":
    app = PromptPlayground()
    app.mainloop()
