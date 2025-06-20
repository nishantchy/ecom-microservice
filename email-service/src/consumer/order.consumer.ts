import amqp from "amqplib";
import { sendOrderConfirmationEmail } from "../service/email.service";
import { orderConfirmationTemplate } from "../utils/email.template";
import EmailLog from "../models/EmailLog";

const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://localhost:5672/";
if (!RABBITMQ_URL) {
  throw new Error("RABBITMQ_URL environment variable is not set");
}

export async function startOrderConsumer() {
  const connection = await amqp.connect(RABBITMQ_URL);
  const channel = await connection.createChannel();
  const queue = "order.created";

  await channel.assertQueue(queue, { durable: true });

  channel.consume(queue, async (msg) => {
    if (msg) {
      try {
        const orderData = JSON.parse(msg.content.toString());
        const html = orderConfirmationTemplate({
          userName: orderData.user_name,
          orderNumber: orderData.order_number,
          totalAmount: orderData.total_amount,
          items: orderData.items,
          paymentMethod: orderData.payment_method,
        });

        await sendOrderConfirmationEmail(
          orderData.user_email,
          "Order Confirmation",
          html
        );

        await EmailLog.create({
          to: orderData.user_email,
          subject: "Order Confirmation",
          html,
          status: "sent",
          metadata: orderData,
        });

        channel.ack(msg);
        console.log("Order confirmation email sent to:", orderData.user_email);
      } catch (error: any) {
        console.error("Failed to process order.created message:", error);
        channel.nack(msg, false, false);
      }
    }
  });

  console.log("Order consumer started, waiting for messages...");
}
