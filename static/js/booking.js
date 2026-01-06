document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("booking-form");
    const successMsg = document.getElementById("success-msg");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        const res = await fetch("/book", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        if (data.success) {
            successMsg.style.display = "block";
            form.reset();
        } else {
            alert(data.message);
        }
    });
});
