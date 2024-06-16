# app/emails/email_templates.py

registration_verification = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registration Verification</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">

    <div style="background-color: #f8f8f8; padding: 20px;">
        <h2 style="text-align: center; color: #333;">Welcome to Our Online Store!</h2>
    </div>

    <div style="padding: 20px;">
        <p style="font-size: 16px;">Hi {username},</p>
        <p style="font-size: 16px;">Thank you for registering with us! To verify your email address, please click on the following link:</p>
        <p style="font-size: 16px;"><a href="{verification_link}" style="background-color: #007bff; color: #fff; padding: 10px 20px; text-decoration: none;">Verify Email</a></p>
        <p style="font-size: 16px;">If you did not sign up for an account, please ignore this email.</p>
        <p style="font-size: 16px;">Best regards,</p>
        <p style="font-size: 16px;">The Team</p>
    </div>

</body>
</html>
"""

order_confirmation = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Confirmation</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">

    <div style="background-color: #f8f8f8; padding: 20px;">
        <h2 style="text-align: center; color: #333;">Order Confirmation</h2>
    </div>

    <div style="padding: 20px;">
        <p style="font-size: 16px;">Hi {username},</p>
        <p style="font-size: 16px;">Thank you for your order! Your order details are as follows:</p>
        <ul style="font-size: 16px;">
            <li>Order ID: {order_id}</li>
            <li>Total Amount: {total_amount}</li>
            <li>Order Status: {status}</li>
        </ul>
        <p style="font-size: 16px;">For further assistance, please contact us.</p>
        <p style="font-size: 16px;">Best regards,</p>
        <p style="font-size: 16px;">The Team</p>
    </div>

</body>
</html>
"""
