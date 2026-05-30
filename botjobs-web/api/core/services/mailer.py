def send_custom_email(email_body):
    print("--> [Mailer] Configurando SMTP nativo...")
    
    # Aquí usarás la librería nativa 'smtplib' y 'email.message'
    print("\n--- CORREO ENVIADO ---")
    print(email_body)
    print("----------------------\n")
    
    return True