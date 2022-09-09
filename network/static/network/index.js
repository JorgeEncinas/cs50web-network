document.addEventListener('DOMContentLoaded', function() {

const newpost_form = document.getElementById("new-post");

newpost_form.addEventListener('submit', submit_post);

})

async function set_alert(className, message) {
    let alert_area = document.getElementById("alert-area")
    alert_area.className = `alert alert-${className}`
    alert_area.role = `alert`
    alert_area.innerHTML = message
    alert_area.style.display = 'block';
  
    await new Promise(resolve => setTimeout(resolve, 3000))
    alert_area.style.display = 'none';
}
  
//This is from this answer: https://stackoverflow.com/a/39914235
//I wanted to use a timeout before disappearing the alert
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

function submit_post(event) {
    event.preventDefault();
    let textVarElmt = document.getElementById("new-post-textarea")
    let textVar = textVarElmt.value
    if (textVar.trim().length <= 0) {
        set_alert("danger", "Post is empty!")
    }
    else {
        //console.log(JSON.stringify(
        //    {text:textVar}))
        fetch("/new_post", {
            method:"POST",
            body: JSON.stringify({
                text:textVar
            })
        })
        .then(response => response.json())
        .then(message => {
            //console.log(message)
            if(message.posted) {
                //console.log(message)
                set_alert('success', 'post successful!')
                let textVarElmt = document.getElementById("new-post-textarea")
                textVarElmt.value = ""
                let post_content = document.getElementById("post_content")
                //This seems easier to code if I was using react.
                //Alas, without React, it's quite a handful.
                let post = message.post
                let user = message.user
                let timestamp = message.timestamp
                //console.log(post)
                //console.log(user)
                let newPost = document.createElement("div")
                newPost.innerHTML = `
                <div class="post-container">
                    <img src="${user[0].profile_image_URL}" class="profile-img">
                    <div>
                        <a href="profile/${user[0].username}"><b>${user[0].public_name}</b></a><h6>@${user[0].username}</h6>
                        <div id="ogpost-${post[0].id}">${post[0].text}</div>
                        <textarea id="textarea-${post[0].id}" style="display:none;"></textarea>
                        <h6><i><span id="edited-${post[0].id}">Posted</span> on <span id="post-timestamp-${post[0].id}">${timestamp}</span></i></h6>
                        <button class="like-btn" onclick="change_like_status(event, ${post[0].id})" id="post-btn-${post[0].id}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16">
                                <path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>
                            </svg>        
                        </button><h6><span id="post-likes-${post[0].id}">0</span> Likes</h6>
                        <div id="edit-link-${post[0].id}">
                            <button type="button" onclick="get_edit_post(${post[0].id})">Edit this post.</button>
                        </div>
                        <div id="edit-btn-area-${post[0].id}" style="display:none;">
                            <button type="button" onclick="post_edit_post(${post[0].id})">Save Changes</button>
                            <button type="button" onclick="cancel_edit_post(${post[0].id})">Cancel Edit</button>
                        </div>
                        <a href="#">Reply</a>
                        <a href="load_post/${post[0].id}">See Replies</a>
                    </div>
                </div>
                `
                post_content.insertBefore(newPost, post_content.children[0]) //Thanks to w3schools.com/jsref/met_node_insertbefore.asp
            } else {
                set_alert('danger', 'error when submitting post.')
            }
        })
        .catch(error => {
            set_alert("danger", error)
            console.log(error)
        })
    }
}

function change_like_status(event, postID) {
    event.preventDefault();
    fetch("/", {
        method:"PUT",
        body: JSON.stringify({
            "postID":postID
        })
    })
    .then(response => response.json()) 
    .then(response => {
        // I actually got stuck here trying to get the data from the JSONResponse, so thank you to...
        // https://forum.freecodecamp.org/t/how-to-use-django-jsonresponse-and-javascript-fetch/470637/2
        if (response.status == 404) {
            set_alert("danger", response.message)
        }
        else {
            post_btn = document.getElementById(`post-btn-${postID}`)
            post_likes = document.getElementById(`post-likes-${postID}`)
            post_likes.innerHTML = response.like_count        
            if (response.liked === true) {
                post_btn.innerHTML=`
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-heart-fill" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
                </svg>`   
            } else {
                post_btn.innerHTML=`
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16">
                        <path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>
                    </svg>`
            }
        }
    })
    .catch(error => {
        set_alert("danger", error)
        console.log(error)
    })
}

function change_follow_status(userID) {
    fetch(`/profile/${userID}`, {
        method: "PUT"
    })
    .then(response => response.json())
    .then(response => {
        if (response.status == 404) {
            set_alert("danger", "User not found")
        } else {
            let follow_btn = document.getElementById("follow-btn")
            let follower_count = document.getElementById("follower-count")
            follower_count.innerHTML = response.follower_count
            if (response.follows == true) {
                follow_btn.innerHTML = "Unfollow"
            } else {
                follow_btn.innerHTML = "Follow"
            }
        }
    })
    .catch(error => {
        set_alert("danger", "An unexpected error has occurred.")
        console.log(error)
    })
}

function get_edit_post(postID) {
    let divarea = document.getElementById(`ogpost-${postID}`)
    divarea.style.display = "none"
    let textarea = document.getElementById(`textarea-${postID}`)
    textarea.value = divarea.innerHTML
    textarea.style.display = "block"
    let get_edit = document.getElementById(`edit-link-${postID}`)
    get_edit.style.display = "none"
    let save_edit = document.getElementById(`edit-btn-area-${postID}`)
    save_edit.style.display = "block"
}

function post_edit_post(postID) {
    let textarea = document.getElementById(`textarea-${postID}`)
    let postarea = document.getElementById(`ogpost-${postID}`)
    if (textarea.value.length < 1) {
        set_alert("danger", "Post is empty.")
    } else if (postarea.innerHTML == textarea.value) {
        set_alert("danger", "No changes were made.")
        cancel_edit_post(postID)
    } else {
        fetch(`/edit_post/${postID}`, {
            method:"POST",
            body: JSON.stringify({
                "text": textarea.value
            })
        })
        .then(response => response.json())
        .then(response => {
            if (response.edited) {
                textarea.style.display = "none";
                //console.log(response)
                postarea.innerHTML = response.text
                postarea.style.display = "block";
                document.getElementById(`edited-${postID}`).innerHTML = `<i>Edited</i>`
                document.getElementById(`edit-btn-area-${postID}`).style.display = "none"
                document.getElementById(`edit-link-${postID}`).style.display = "block"
                document.getElementById(`post-timestamp-${postID}`).innerHTML = response.timestamp
            } else {
                set_alert("danger", response.message)
            }   
        })
        .catch(error => {
            console.log(error)
        })
    } 
}

function cancel_edit_post(postID) {
    let textarea = document.getElementById(`ogpost-${postID}`)
    let postarea = document.getElementById(`textarea-${postID}`)
    let edit_btn_area = document.getElementById(`edit-link-${postID}`)
    let save_btn_area = document.getElementById(`edit-btn-area-${postID}`)
    textarea.style.display = "block"
    postarea.style.display = "none"
    save_btn_area.style.display = "none"
    edit_btn_area.style.display = "block"
}
