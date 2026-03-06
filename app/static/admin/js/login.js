document.addEventListener("DOMContentLoaded", function () {

    const input = document.querySelector("#id_password")
    const toggle = document.querySelector("#togglePassword")

    if (!input || !toggle) return

    toggle.addEventListener("click", function () {

        if (input.type === "password") {
            input.type = "text"
            toggle.className = "ri-eye-fill"
        } else {
            input.type = "password"
            toggle.className = "ri-eye-off-fill"
        }

    })

})