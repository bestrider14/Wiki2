
//variable globale pour compt

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

function addReferenceToCreeArticleUI(){
    //console.log("Add reference button was clicked through app.js")
    const nouvelleReference = document.createElement("div");
    nouvelleReference.id = `reference${compteurReference}`;
    nouvelleReference.classList.add('uneReference');

    //pour ajouter des sauts de ligne
    const br = document.createElement("br");

    //nomAuteur
    const nomAuteurInput = document.createElement("input");
    nomAuteurInput.type ='text';
    nomAuteurInput.name =`auteur[${compteurReference}]`;
    nomAuteurInput.placeholder = 'Auteur';
    nouvelleReference.appendChild(nomAuteurInput);
    nouvelleReference.appendChild(br);
    
    //titreDocument
    const titreInput = document.createElement("input");
    titreInput.type ='text';
    titreInput.name =`titre[${compteurReference}]`;
    titreInput.placeholder = 'Titre';
    nouvelleReference.appendChild(titreInput);
    nouvelleReference.appendChild(br);

    //anneeParution
    const anneParutionInput = document.createElement("input");
    anneParutionInput.type ='number';
    const maxYear = new Date().getFullYear();
    anneParutionInput.max=maxYear.toString();
    anneParutionInput.min="0";
    anneParutionInput.name =`anneeParution[${compteurReference}]`;
    anneParutionInput.placeholder = 'Année de Parution';
    nouvelleReference.appendChild(anneParutionInput);
    nouvelleReference.appendChild(br);
    
    //ISBN
    const isbnInput = document.createElement('input');
    isbnInput.type = 'text';
    isbnInput.name = `isbn[${compteurReference}]`
    isbnInput.placeholder = "Entrez le ISBN"
    isbnInput.required = false;
    nouvelleReference.appendChild(isbnInput);
    nouvelleReference.appendChild(br);
    
    //editeur
    const editeurInput = document.createElement("input");
    editeurInput.type ='text';
    editeurInput.name =`editeur[${compteurReference}]`;
    editeurInput.placeholder = 'Éditeur';
    nouvelleReference.appendChild(editeurInput);
    nouvelleReference.appendChild(br);


    document.getElementById('references').appendChild(nouvelleReference);
    //incrémenter le compteur de références
    compteurReference++;
    //console.log("Current value of compteurReference:", compteurReference);
}