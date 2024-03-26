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