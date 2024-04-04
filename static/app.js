const checkIfUserExists = () => {
    const registrationForm = document.forms['inscription_form']
    const emailFormElement = registrationForm['email']
    const email = emailFormElement.value
    if (email.length > 0){
        axios.post('/validate_user_registration', {
        email: email
    }).then((response) => {
        if(response.data.user_exists === "True") {
            console.log(response.data)
            emailFormElement.setCustomValidity("Ce email est déjà utilsé. Veuillez vous connecter.")
            emailFormElement.reportValidity()
        }
        else{
            console.log(response.data)
            emailFormElement.setCustomValidity("")
            emailFormElement.reportValidity()
        }
    }, (error) => {
        console.log(error)
    })
    }

}

function articleLink(id){
    window.location.href = "/article?id="+id;
}

function clearInput(element) {
    if (element.value === "Example Text") {
        element.value = "";
    }
}

function changeUsername() {
    var newUsername = prompt("Enter your new username:");
    if (newUsername !== null && newUsername !== "") {
        document.getElementById("username").textContent = newUsername;
    }
}