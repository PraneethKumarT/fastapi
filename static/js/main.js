// Create-post form: submit to the JSON API, then redirect home.
const form = document.getElementById("post-form");
if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const errorEl = document.getElementById("form-error");
        errorEl.hidden = true;

        const data = new FormData(form);
        const payload = {
            title: data.get("title"),
            content: data.get("content"),
            user_id: Number(data.get("user_id")),
        };

        const res = await fetch("/api/posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (res.ok) {
            const post = await res.json();
            window.location.href = `/post/${post.id}`;
        } else {
            const body = await res.json().catch(() => ({}));
            errorEl.textContent = formatError(body) || "Failed to create post.";
            errorEl.hidden = false;
        }
    });
}

// Delete buttons: confirm, DELETE via the API, then remove the card or redirect.
document.querySelectorAll(".delete-post").forEach((button) => {
    button.addEventListener("click", async () => {
        if (!confirm("Delete this post?")) return;

        const postId = button.dataset.postId;
        const res = await fetch(`/api/posts/${postId}`, { method: "DELETE" });

        if (res.ok) {
            const redirect = button.dataset.redirect;
            if (redirect) {
                window.location.href = redirect;
            } else {
                button.closest("article").remove();
            }
        } else {
            alert("Failed to delete post.");
        }
    });
});

// FastAPI validation errors come back as {detail: [{loc, msg}, ...]} or {detail: "..."}.
function formatError(body) {
    if (!body || !body.detail) return "";
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
        return body.detail.map((e) => e.msg).join(", ");
    }
    return "";
}
