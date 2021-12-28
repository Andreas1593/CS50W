document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields when composing new email
  if (!email.id) {
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }
  // Pre-fill composition fields when replying to an email
  else {
    document.querySelector('#compose-recipients').value = email.sender;

    if (email.subject.slice(0, 4) === "Re: ") {
      document.querySelector('#compose-subject').value = email.subject;
    }
    else {
      document.querySelector('#compose-subject').value = "Re: " + email.subject;
    }

    document.querySelector('#compose-body').value = "\n\n\n------ On " +
        email.timestamp + " " + email.sender + " wrote: " + "------\n\n" + email.body;
  }

  // Send email when submitting
  document.querySelector('#compose-form').onsubmit = () => {
    send_email();
    return false;
  }
}


function send_email() {

  const recipients =  document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body,
    })
  })
  .then(response => response.json())
  .then(result => {
      load_mailbox('sent');
  });
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Clear emails view
  document.querySelector('#emails-view').innerHTML = '';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

      emails.forEach(email => {
        const emailDiv = createEmailDiv(email);

        // Add event listener to email div
        emailDiv.addEventListener('click', () => {
          load_email(email.id);
        })

        // Append email div to the page
        document.querySelector('#emails-view').append(emailDiv);
      });
  });
}

function load_email(id) {

  // Show email view and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';

  // Clear email view
  document.querySelector('#email-view').innerHTML = "";

  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {

        // Create HTML and fill tags with email data
        const emailViewDiv = createEmailViewDiv(email);

        // Mark email as read
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
              read: true
          })
        });

        // Append the email to the email view
        document.querySelector('#email-view').append(emailViewDiv);
      });
}


function createEmailDiv(email) {

  // Create div that contains an email
  const emailDiv = document.createElement('div');
  emailDiv.classList.add("email");

  // Change background color of read emails
  if (email.read) {
    emailDiv.classList.add("read");
  }
  else {
    emailDiv.classList.remove("read");
  }

  // Create first row div with containing divs
  const senderDiv = document.createElement('div');
  senderDiv.classList.add("row-div");

  const sender1 = document.createElement('p');
  sender1.innerHTML = "FROM:";
  sender1.classList.add("description");
  const sender2 = document.createElement('p');
  sender2.innerHTML = email.sender;
  sender2.classList.add("content");

  senderDiv.append(sender1, sender2);

  // Create second row div with containing divs
  const subjectDiv = document.createElement('div');
  subjectDiv.classList.add("row-div");

  const subject1 = document.createElement('p');
  subject1.innerHTML = "Subject:";
  subject1.classList.add("description");
  const subject2 = document.createElement('p');
  subject2.innerHTML = email.subject;
  subject2.classList.add("content");

  subjectDiv.append(subject1, subject2);

  // Create third row div with containing divs
  const timestampDiv = document.createElement('div');
  timestampDiv.classList.add("row-div");

  const timestamp1 = document.createElement('p');
  timestamp1.innerHTML = "Timestamp:";
  timestamp1.classList.add("description");
  const timestamp2 = document.createElement('p');
  timestamp2.innerHTML = email.timestamp;
  timestamp2.classList.add("content");

  timestampDiv.append(timestamp1, timestamp2);

  // Append all row divs to email div
  emailDiv.append(senderDiv, subjectDiv, timestampDiv);

  return emailDiv;
}


function createEmailViewDiv(email) {

  // Create div that contains an email
  const emailViewDiv = document.createElement('div');

  // Create first row div with containing divs
  const senderDiv = document.createElement('div');
  senderDiv.classList.add("row-div");

  const sender1 = document.createElement('p');
  sender1.innerHTML = "FROM:";
  sender1.classList.add("description");
  const sender2 = document.createElement('p');
  sender2.innerHTML = email.sender;
  sender2.classList.add("content");

  senderDiv.append(sender1, sender2);

  // Create second row div with containing divs
  const recipientDiv = document.createElement('div');
  recipientDiv.classList.add("row-div");

  const recipient1 = document.createElement('p');
  recipient1.innerHTML = "TO:";
  recipient1.classList.add("description");
  const recipient2 = document.createElement('p');
  recipient2.innerHTML = email.subject;
  recipient2.classList.add("content");

  recipientDiv.append(recipient1, recipient2);
  
  // Create third row div with containing divs
  const subjectDiv = document.createElement('div');
  subjectDiv.classList.add("row-div");

  const subject1 = document.createElement('p');
  subject1.innerHTML = "Subject:";
  subject1.classList.add("description");
  const subject2 = document.createElement('p');
  subject2.innerHTML = email.subject;
  subject2.classList.add("content");

  subjectDiv.append(subject1, subject2);

  // Create fourth row div with containing divs
  const timestampDiv = document.createElement('div');
  timestampDiv.classList.add("row-div");

  const timestamp1 = document.createElement('p');
  timestamp1.innerHTML = "Timestamp:";
  timestamp1.classList.add("description");
  const timestamp2 = document.createElement('p');
  timestamp2.innerHTML = email.timestamp;
  timestamp2.classList.add("content");

  timestampDiv.append(timestamp1, timestamp2);

  // Create fifth row div with containing buttons
  const buttonDiv = document.createElement('div');
  // Not for emails from the sent mailbox
  const user = document.querySelector("h2").innerHTML;
  if (user != email.sender) {

    const archiveButton = document.createElement('button');
    if (email.archived) {
      archiveButton.innerHTML = "Unarchive";
      archiveButton.classList.add("btn", "btn-danger", "email-buttons");
    }else {
      archiveButton.innerHTML = "Archive";
      archiveButton.classList.add("btn", "btn-secondary", "email-buttons");
    }

    // Add event listener to archive / unarchive button
    archiveButton.addEventListener("click", () => {

      archiveEmail(email);
      setTimeout(function() { load_mailbox("inbox"); }, 100);
    });

    const replyButton = document.createElement('button');
    replyButton.classList.add("btn", "btn-success", "email-buttons");
    replyButton.innerHTML = "Reply";

    // Add event listener to reply button
    replyButton.addEventListener("click", () => {

      compose_email(email);
    })
    
    buttonDiv.append(replyButton, archiveButton);
  }

  // Create horizontal rule
  const hr = document.createElement('hr');

  // Create paragraph for email content
  const emailContent = document.createElement('div');
  emailContent.classList.add("email-body");
  emailContent.innerHTML = email.body;

  // Append all row divs to email view div
  emailViewDiv.append(senderDiv, recipientDiv, subjectDiv, timestampDiv, buttonDiv, hr, emailContent);

  return emailViewDiv;
}


function archiveEmail(email) {

  // Mark email as archived / unarchived
  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: !email.archived,
    })
  });
}