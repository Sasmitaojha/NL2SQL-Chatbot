import requests
import json

def chat():
    print("===========================================")
    print("   Clinic NL2SQL Terminal Chat Interface   ")
    print("===========================================")
    print("Type 'exit' to quit.\n")
    
    while True:
        question = input("You: ")
        if question.lower().strip() == 'exit':
            break
            
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat", 
                json={"question": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("\n[AI Message]:", data.get("message"))
                
                sql = data.get("sql_query")
                if sql:
                    print(f"[SQL Generated]: {sql}")
                    
                rows = data.get("rows")
                if rows:
                    print(f"\n[Data Returned] ({data.get('row_count')} rows):")
                    columns = data.get("columns", [])
                    if columns:
                        print(f"Columns: {', '.join(columns)}")
                    
                    for i, row in enumerate(rows[:5]): # show up to 5
                        print(f" - {row}")
                    if len(rows) > 5:
                        print(" ... (Output truncated)")
                        
            else:
                print(f"\n[Server Error {response.status_code}]: {response.text}")
                
        except Exception as e:
            print(f"\n[Connection Error]: Could not reach the server. Is it running? ({e})")
            
        print("-" * 50)

if __name__ == "__main__":
    chat()
