const checkIfUserExists = () => {
    const registrationForm = document.forms['inscription_form']
    const emailFormElement = registrationForm['email']
    const email = emailFormElement.value
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

function articleLink(id){
    window.location.href = "/article?id="+id;
}

function up()  {
    let statusElement = document.getElementById("up-status");
    statusElement.innerHTML = "Création en cours..."

    fetch("/up", {
        method: "POST"
    }).then(function(response) {
        if (response.status === 200) {
            statusElement.innerHTML = "<p style='color:green'>Création réussie. Cliquez sur rafraîchir pour voir le nouveau contenu de la BD.</p>"
        } else {
            statusElement.innerHTML = "<p style='color:red'>Échec. Une erreur est survenue lors de la création. Référez-vous à l'erreur dans votre IDE.</p>"
        }

        setTimeout(function(){
            window.location.reload();
        }, 3000);
    })
}

