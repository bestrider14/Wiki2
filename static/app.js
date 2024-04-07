
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
            emailFormElement.setCustomValidity("Ce email est déjà utilsé. Veuillez vous connecter.")
            emailFormElement.reportValidity()
        }
        else{
            emailFormElement.setCustomValidity("")
            emailFormElement.reportValidity()
        }
    }, (error) => {
        console.log(error)
    })
    }

}


const checkUserRole = () => {
    const updateForm = document.forms['update_user']
    const emailFormElement = updateForm['email']
    const email = emailFormElement.value
    if (email.length > 0){
        axios.post('/get_user_role', {
        email: email
    }).then((response) => {
        document.getElementById("selectRole").value = response.data.user_role;
    }, (error) => {
        console.log(error)
    })
    }
}

function confirmDelete() {
    const confirmed = confirm("Êtes-vous certain de vouloir supprimer votre compte?");
    if (confirmed) {
        document.getElementById("deleteForm").submit();
    } else {
        return false;
    }
}

function confirmUp() {
    const confirmed = confirm("Êtes-vous certain refaire la basse de données");
    if (confirmed) {
        document.getElementById("upForm").submit();
    } else {
        return false;
    }
}

function articleLink(id){
    window.location.href = "/article?id="+id;
}


function changeUsername() {
    const newUsername = prompt("Enter your new username:");
    if (newUsername !== null && newUsername !== "") {
        document.getElementById("username").textContent = newUsername;
    }
}

function addReferenceToCreeArticleUI(){
    //console.log("Add reference button was clicked through app.js")
    const nouvelleReference = document.createElement("div");
    nouvelleReference.id = `reference${compteurReference}`;
    nouvelleReference.classList.add('uneReference');

    //nomAuteur
    const nomAuteurInput = document.createElement("input");
    nomAuteurInput.type ='text';
    nomAuteurInput.name =`auteur[${compteurReference}]`;
    nomAuteurInput.placeholder = 'Auteur';
    nouvelleReference.appendChild(nomAuteurInput);
    
    //titreDocument
    const titreInput = document.createElement("input");
    titreInput.type ='text';
    titreInput.name =`titre[${compteurReference}]`;
    console.log(titreInput.name)
    titreInput.placeholder = 'Titre';
    nouvelleReference.appendChild(titreInput);

    //anneeParution
    const anneParutionInput = document.createElement("input");
    anneParutionInput.type ='number';
    const maxYear = new Date().getFullYear();
    anneParutionInput.max=maxYear.toString();
    anneParutionInput.min="0";
    anneParutionInput.name =`anneeParution[${compteurReference}]`;
    anneParutionInput.placeholder = 'Année de Parution';
    nouvelleReference.appendChild(anneParutionInput);
    
    //ISBN
    const isbnInput = document.createElement('input');
    isbnInput.type = 'text';
    isbnInput.name = `isbn[${compteurReference}]`
    isbnInput.placeholder = "Entrez le ISBN"
    isbnInput.required = false;
    nouvelleReference.appendChild(isbnInput);
    
    //editeur
    const editeurInput = document.createElement("input");
    editeurInput.type ='text';
    editeurInput.name =`editeur[${compteurReference}]`;
    editeurInput.placeholder = 'Éditeur';
    nouvelleReference.appendChild(editeurInput);


    document.getElementById('references').appendChild(nouvelleReference);
    //incrémenter le compteur de références
    compteurReference++;
    document.getElementById('referenceCount').value = compteurReference;
    //console.log("Current value of compteurReference:", compteurReference);
}