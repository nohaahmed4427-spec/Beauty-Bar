async function loadServices() {

    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/services"
            );


        if (!response.ok) {
            throw new Error(
                "Failed to load services"
            );
        }


        const data =
            await response.json();


        const servicesContainer =
            document.getElementById("services");


        servicesContainer.innerHTML = "";


        const serviceInfo = {

            "Facial Care": {
                icon: "✦",
                text: "Care made for a fresh and beautiful skin routine."
            },

            "Acne Care": {
                icon: "♡",
                text: "Explore products selected for acne-prone skin."
            },

            "Skin Hydration": {
                icon: "◇",
                text: "Hydrating products for soft, comfortable skin."
            },

            "Skin Cleansing": {
                icon: "✧",
                text: "Discover products for a clean and refreshed routine."
            },

            "Sun Protection": {
                icon: "☼",
                text: "Explore products designed for everyday sun protection."
            }

        };


        data.services.forEach(
            function (service) {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "service-card";


                const info =
                    serviceInfo[service] || {
                        icon: "♡",
                        text: "Discover our skin care collection."
                    };


                card.innerHTML = `

                    <div class="service-icon">
                        ${info.icon}
                    </div>

                    <h3>
                        ${service}
                    </h3>

                    <p>
                        ${info.text}
                    </p>

                `;


                card.addEventListener(
                    "click",
                    function () {

                        window.location.href =
                            "products.html?category="
                            +
                            encodeURIComponent(
                                service
                            );

                    }
                );


                servicesContainer.appendChild(
                    card
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Error loading services:",
            error
        );

    }

}


loadServices();