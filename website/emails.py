from flask import url_for

def confirm_mail_text(token):
    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Confirm Email</title>

</head>
<body style="margin: 0;background-color: #ecf0f1;">


<center class="wrapper" style="width: 100%;table-layout: fixed;background-color: #ecf0f1;padding-bottom: 60px;">
	<table class="main" width="100%" style="border-spacing: 0;background-color: #ffffff;margin: 0 auto;width: 100%;max-width: 600px;font-family: sans-serif;color: #4a4a4a;">
		<tr>
			<td height="8" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>

<tr>
	<td style="padding: 14px 0 4px;">
		<table width="100%" style="border-spacing: 0;">
			<tr>
				<td class="two-columns" style="padding: 0;text-align: center;font-size: 0;">
					<table class="column" style="border-spacing: 0;width: 100%;max-width: 300px;display: inline-block;vertical-align: center;">
						<tr>
							<td style="padding: 0 0 15px 60px;">
								<a href="https://yourprojecttracker.com/"><img src="{{ url_for('static', filename='ypt_logo.svg') }}" alt="logo" width="50" title="logo" style="border: 0;"></a>
							</td>
						</tr>
					</table>
					<table class="column" style="border-spacing: 0;width: 100%;max-width: 300px;display: inline-block;vertical-align: center;">
						<tr>
							<td style="padding: 0;">
								<p style="font-size: 26px; font-weight: bold; padding-right: 40px;"><a style="text-decoration: none; color: #2c3e50;" href="https://yourprojecttracker.com/">Your Project Tracker</a></p>
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
	</td>
</tr>
		<tr>
			<td height="1" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>


		<tr>
			<td style="padding: 5px 0 50px;">
				<table width="100%" style="border-spacing: 0;">
					<tr>
						<td style="text-align: center; padding: 15px 0 0 0;">
							<p style="font-size: 15px; line-height: 23px; padding: 20px 0 0;">Welcome!</p>
							<p style="font-size: 15px; line-height: 23px; padding: 0 5px;">Your Project Tracker is a minimalistic web-app to measure time you spend on your projects and track your progress with useful infographics.</p>
							<p style="font-size: 15px; line-height: 23px; padding: 0 5px 30px;">To start using the app, please confirm your email:</p>
							<a href="{url_for('auth.confirm_email', token=token, _external=True)}" class="button" style="background-color: #2c3e50;color: #ffffff;text-decoration: none;padding: 12px 20px;font-weight: bold;border-radius: 5px;">Confirm Email</a>
							<p style="font-size: 15px; line-height: 23px; padding: 30px 5px 0;">If you did not signup for <a style="text-decoration: none; color: #2c3e50;" href="https://yourprojecttracker.com/"><strong>yourprojecttracker.com</strong></a>, please ignore this email.</p>
						</td>
					</tr>
				</table>
			</td>
		</tr>

		<tr>
			<td height="8" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>
	</table>
</center>
</body>
</html>
'''

def reset_email_text(token):
    return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reset Email</title>

</head>
<body style="margin: 0;background-color: #ecf0f1;">

<center class="wrapper" style="width: 100%;table-layout: fixed;background-color: #ecf0f1;padding-bottom: 60px;">
	<table class="main" width="100%" style="border-spacing: 0;background-color: #ffffff;margin: 0 auto;width: 100%;max-width: 600px;font-family: sans-serif;color: #4a4a4a;">
		<tr>
			<td height="8" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>

<tr>
	<td style="padding: 14px 0 4px;">
		<table width="100%" style="border-spacing: 0;">
			<tr>
				<td class="two-columns" style="padding: 0;text-align: center;font-size: 0;">
					<table class="column" style="border-spacing: 0;width: 100%;max-width: 300px;display: inline-block;vertical-align: center;">
						<tr>
							<td style="padding: 0 0 15px 60px;">
								<a href="https://yourprojecttracker.com/"><img src="{{ url_for('static', filename='ypt_logo.svg') }}" alt="logo" width="50" title="logo" style="border: 0;"></a>
							</td>
						</tr>
					</table>
					<table class="column" style="border-spacing: 0;width: 100%;max-width: 300px;display: inline-block;vertical-align: center;">
						<tr>
							<td style="padding: 0;">
								<p style="font-size: 26px; font-weight: bold; padding-right: 40px;"><a style="text-decoration: none; color: #2c3e50;" href="https://yourprojecttracker.com/">Your Project Tracker</a></p>
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
	</td>
</tr>
		<tr>
			<td height="1" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>

		<tr>
			<td style="padding: 5px 0 50px;">
				<table width="100%" style="border-spacing: 0;">
					<tr>
						<td style="text-align: center; padding: 15px 0 0 0;">
							
							<p style="font-size: 15px; line-height: 23px; padding: 30px 10px 30px;">You requested a password reset on <a style="text-decoration: none; color: #2c3e50;" href="https://yourprojecttracker.com/"><strong>yourprojecttracker.com</strong></a></p>
							<a href="{url_for('views.reset_token', token=token, _external=True)}" class="button" style="background-color: #2c3e50;color: #ffffff;text-decoration: none;padding: 12px 20px;font-weight: bold;border-radius: 5px;">Reset Password</a>
							<p style="font-size: 15px; line-height: 23px; padding: 30px 5px 0;">If you did not make this password reset request, please ignore this email.</p>
						</td>
					</tr>
				</table>
			</td>
		</tr>

		<tr>
			<td height="8" style="background-color: #2c3e50;padding: 0;"></td>
		</tr>
	</table>
</center>

</body>
</html>
'''