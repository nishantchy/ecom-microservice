import nodemailer from "nodemailer";

let transporter: nodemailer.Transporter | null = null;

function initializeTransporter(): nodemailer.Transporter {
  if (!transporter) {
    const EMAIL_USER = process.env.EMAIL_USER;
    const EMAIL_PASS = process.env.EMAIL_PASS;

    console.log("Initializing email transporter...");
    console.log("EMAIL_USER:", EMAIL_USER ? "Set" : "Not set");
    console.log("EMAIL_PASS:", EMAIL_PASS ? "Set" : "Not set");

    if (!EMAIL_USER || !EMAIL_PASS) {
      throw new Error(
        "EMAIL_USER and EMAIL_PASS must be set in environment variables"
      );
    }

    transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: EMAIL_USER,
        pass: EMAIL_PASS,
      },
    });

    console.log("Email transporter initialized successfully");
  }

  return transporter;
}

export async function sendOrderConfirmationEmail(
  to: string,
  subject: string,
  html: string
) {
  try {
    const transporterInstance = initializeTransporter();
    const EMAIL_USER = process.env.EMAIL_USER;

    const mailOptions = {
      from: EMAIL_USER,
      to,
      subject,
      html,
    };

    console.log(`Sending email to: ${to}`);
    const result = await transporterInstance.sendMail(mailOptions);
    console.log("Email sent successfully:", result.messageId);
    return result;
  } catch (error) {
    console.error("Failed to send email:", error);
    throw error;
  }
}
