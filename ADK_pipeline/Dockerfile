# 1️⃣ Use a lightweight Python base
FROM python:3.13.9-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy dependency file first (for layer caching)
COPY requirements.txt .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy all project files
COPY . .

# 6️⃣ Ensure the data folder exists (for SQLite DB)
RUN mkdir -p data/db_files

# 7️⃣ Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1
ENV PATH="/app:${PATH}"

# 8️⃣ Default command — run your main entry script
CMD ["python", "inventory_agent/main.py"]
