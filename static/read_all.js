function read_all(){
    wrapper = document.getElementById('add_notification')
    wrapper.innerHTML = ` <a class="dropdown-item" id='no-new' href="#">No new notifications</a>`
    wrapper.innerHTML += ` <a class="dropdown-item" onclick='read_all()'>Mark all as read</a>`

    var url = '/chat/api/notification/read_all'

    fetch(url)
    .then((resp) => resp.json())
    .then(function(data){
        console.log('Ok')
    })
}
