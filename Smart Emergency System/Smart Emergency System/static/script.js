document.addEventListener(
    "DOMContentLoaded",
    function () {

        const flashes =
            document.querySelectorAll(
                ".flash"
            );


        flashes.forEach(
            function (flash) {

                setTimeout(
                    function () {

                        flash.style.opacity =
                            "0";

                        flash.style.transform =
                            "translateX(30px)";

                        flash.style.transition =
                            "0.4s";

                    },
                    4000
                );

            }
        );

    }
);