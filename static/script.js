function autoComplete() {
    let q = document.getElementById("cityInput").value;

    if (q.length < 2) return;

    fetch(`/cities?q=${q}`)
        .then(res => res.json())
        .then(data => {
            let list = document.getElementById("list");
            list.innerHTML = "";

            data.forEach(city => {
                let li = document.createElement("li");
                li.innerText = city;

                li.onclick = () => {
                    document.getElementById("cityInput").value = city;
                    list.innerHTML = "";
                };

                list.appendChild(li);
            });
        });
}

function getWeather() {
    let city = document.getElementById("cityInput").value;

    fetch(`/weather?city=${city}`)
        .then(res => res.json())
        .then(data => {

            if (data.error) {
                document.getElementById("result").innerHTML =
                    "❌ City not found";
                return;
            }

            document.getElementById("result").innerHTML = `
                <div class="label">🌍 City:</div> ${data.city}<br>
                <div class="label">🌡 Temperature:</div> ${data.temp}°C<br>
                <div class="label">⛅ Condition:</div> ${data.condition}<br><br>

                <div class="label">👕 Clothes:</div> ${data.outfit.clothes}<br>
                <div class="label">👟 Shoes:</div> ${data.outfit.shoes}<br>
                <div class="label">🧢 Accessories:</div> ${data.outfit.accessories}<br>

                <!-- 🖼 IMAGE (NEW) -->
                <img class="weather-img" src="${data.outfit.image}">
            `;

            // 🔊 Voice
            let speech = new SpeechSynthesisUtterance(
                `${data.city} is ${data.temp} degrees with ${data.condition}`
            );
            speechSynthesis.speak(speech);
        });
}