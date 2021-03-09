openssl genrsa -out key.pem 4096
# az
openssl req -x509 -new -key key.pem -out az.pem -days 365 -subj '/CN=az' --nodes -addext "subjectAltName = DNS:az"
