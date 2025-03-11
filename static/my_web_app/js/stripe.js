// Stripe

console.log("Sanity Check")



// Get Stripe publishable key
fetch("/stripe_config")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js

  console.log(data)

  const stripe = Stripe(data.publicKey);

  console.log(stripe)

  // new
  // Event handler
  document.querySelector("#submitBtn").addEventListener("click", async () => {
    // Get Checkout Session ID
    const response = await fetch("/create-checkout-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const data = await response.json();
    console.log(data);
    // Redirect to Stripe Checkout
    return stripe.redirectToCheckout({ sessionId: data.sessionId });

  });
});