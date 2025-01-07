function updateImages() {
    const selectedTimestamp = document.getElementById("image-select").value;
    window.location.href = `/dashboard?timestamp=${selectedTimestamp}`;
}

function openimgmodel(src) {
    const modal = document.getElementById("image-imgmodel");
    const modalImage = document.getElementById("imgmodel-image");
    modal.style.display = "block";
    modalImage.src = src;
}

function closeimgmodel() {
    const modal = document.getElementById("image-imgmodel");
    modal.style.display = "none";
}

function sendEmail() {
    const email = document.getElementById("recipient-email").value;
    if (!email) {
        alert("Please enter a valid email address.");
        return;
    }

    const originalImage = document.getElementById("original-image").src.split("/static/")[1];
    const annotatedImage = document.getElementById("annotated-image").src.split("/static/")[1];

    console.log("Original Image Path:", originalImage);
    console.log("Annotated Image Path:", annotatedImage);

    fetch("/send_email", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email,
            original_image: originalImage,
            annotated_image: annotatedImage,
        }),
    })
        .then((response) => {
            if (response.ok) {
                alert("Email sent successfully!");
            } else {
                alert("Failed to send email. Please try again.");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while sending the email.");
        });
}


window.onclick = function(event) {
    const imgmodel = document.getElementById('image-imgmodel');
    if (event.target == imgmodel) {
        imgmodel.style.display = 'none';
    }
}