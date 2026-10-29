FROM python:3.11-slim
LABEL maintainer="vecesta.co@gmail.com"
WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/
COPY fixtures/ ./fixtures/
RUN pip install --no-cache-dir -e .
EXPOSE 8080
ENTRYPOINT ["safe-sql"]
CMD ["serve", "--port", "8080"]
