document.addEventListener("DOMContentLoaded", function() {

    // Iterate over all posts in the document
    document.querySelectorAll(".post").forEach(post => {

        const postId = post.getAttribute("value");


        const editButton = post.querySelector(".post__edit-button");
        if (editButton) {
            editButton.addEventListener("click", () => {

                // Create textarea and pre-fill it with the posts content
                const content = post.querySelector(".post__content")
                const textarea = document.createElement("textarea");
                textarea.className = "form-control edit-post__textarea";
                textarea.innerHTML = content.innerHTML;

                // Replace content with pre-filled textarea for editing
                content.parentNode.replaceChild(textarea, content);

                // Unhide "Save" button
                saveButton = post.querySelector(".post__save-button")
                saveButton.style.visibility = "visible";
                saveButton.addEventListener("click", () => {
                    
                    // Re-replace textarea with new content
                    content.innerHTML = textarea.value;
                    textarea.parentNode.replaceChild(content, textarea);

                    // Hide buttons again
                    saveButton.style.visibility = "hidden";
                    cancelButton.style.visibility = "hidden";

                    // Save change in the backend
                    fetch(`/posts/${postId}`, {
                        method: "PUT",
                        body: JSON.stringify({
                            content: content.innerHTML,
                        })
                    });
                });

                // Unhide "Cancel" button
                cancelButton = post.querySelector(".post__cancel-button")
                cancelButton.style.visibility = "visible";
                cancelButton.addEventListener("click", () => {
                    
                    // Re-replace textarea with original content
                    textarea.parentNode.replaceChild(content, textarea);

                    // Hide buttons again
                    cancelButton.style.visibility = "hidden";
                    saveButton.style.visibility = "hidden";
                });
            });
        }


        const likeButton = post.querySelector("i.fa-thumbs-up")
        likeButton.addEventListener("click", async (event) => {
            
            // Add animation class and remove it when finished
            likeButton.classList.add("fa-thumbs-up-active");
            likeButton.addEventListener("animationend", () => {
                likeButton.classList.remove("fa-thumbs-up-active");
            })

            // Add like
            if (likeButton.classList.contains("fa-thumbs-down")) {
                await fetch(`/likes/${postId}`, {
                    method: "POST",
                })
            }
            
            // Remove like
            else {
                await fetch(`/likes/${postId}`, {
                    method: "DELETE",
                });
            }

            // Toggle "like" button
            likeButton.classList.toggle("fa-thumbs-down");

            // Update displayed like count
            // [Was added later]
            $(`#_likeCounter-container${postId}`).load(`/_likeCounter/${postId}`);
        });


        const commentButton = post.querySelector(".post__comment-button");
        commentButton.addEventListener("click", async() => {

            // Collect all information for saving the comment 
            const textarea = post.querySelector("textarea[name='comment']");

            // Save change in the backend
            await fetch(`/_comments/${postId}`, {
                method: "POST",
                body: JSON.stringify({
                    comment: textarea.value,
                })
            });

            // Refresh comments
            $(`#_comment-container${postId}`).load(`/_comments/${postId}`);

            // Clear comment textarea
            textarea.value = "";

            // Update comment count
            var commentCount = 0;
            commentCount = parseInt(post.querySelector(".comment-count").innerHTML);
            commentCount += 1;
            post.querySelector(".comment-count").innerHTML = commentCount;
        });

    });
});