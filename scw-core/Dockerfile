# Étape 1 : Build du binaire
FROM golang:1.23-alpine as builder

WORKDIR /app

# Copie du code source local
COPY main.go .

# Initialisation locale sans dépendances tierces
RUN go mod init scw-core
RUN go mod tidy

# Build statique pur
ENV CGO_ENABLED=0
ENV GOOS=linux
RUN go build -ldflags="-w -s" -o core main.go

# Étape 2 : Image finale d'exécution minimaliste
FROM alpine:latest
RUN apk add --no-cache ca-certificates

WORKDIR /app

COPY --from=builder /app/core .

EXPOSE 8080
CMD ["./core"]