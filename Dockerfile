FROM nikolaik/python-nodejs:python3.10-nodejs18

WORKDIR /app

RUN apt-get update && apt-get install -y git git-lfs && rm -rf /lib/apt/lists/*

COPY package*.json ./
RUN npm ci --omit=dev

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r backend/requirements.txt

COPY . .

EXPOSE 7860

CMD node server.js & python backend/app.py
