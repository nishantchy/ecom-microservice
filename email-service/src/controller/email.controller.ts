import { Request, Response } from "express";
import { sendOrderConfirmationEmail } from "../service/email.service";
import EmailLog from "../models/EmailLog";

export const sendOrderConfirmation = async (req: Request, res: Response) => {
  const { to, subject, html, metadata } = req.body;
  try {
    const info = await sendOrderConfirmationEmail(to, subject, html);
    await EmailLog.create({
      to,
      subject,
      html,
      status: "sent",
      metadata,
    });
    res.status(200).json({ message: "Email sent", info });
  } catch (error: any) {
    await EmailLog.create({
      to,
      subject,
      html,
      status: "failed",
      metadata,
    });
    res
      .status(500)
      .json({ message: "Failed to send email", error: error.message });
  }
};
