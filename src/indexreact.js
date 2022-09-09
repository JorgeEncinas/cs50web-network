class NewPost extends React.Component {
    submitPost(e) {
        e.preventDefault();
        let textVar = document.getElementById("postform-text")
        fetch("/new_post", {
            method:"POST",
            body: JSON.stringify({
                text:textVar
            })
        })
        .then(response => response.json())
        .then((message) => {
            if(message.posted) {
                return(
                    <div class="alert alert-success">
                        Posted successfully!
                    </div>
                )
            } else {
                return(
                    <div class="alert alert-danger">
                        An error has occurred!
                    </div>
                )
            }
        })
        .catch(error => {
            return (
                <div class="alert alert-danger">
                    {error}
                </div>
            )
        })
    }

    render() {
        return (
        <form onSubmit={this.submitPost}>
            <textarea id="postform-text" placeholder="What are you thinking?"></textarea>
            <input type="submit" value="Post" />
        </form>
        )
    }
}

const npdiv = document.getElementById("new-post")
ReactDOM.render(<NewPost />, npdiv)