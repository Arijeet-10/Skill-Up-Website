form.addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission
   errorMessageDiv.style.display = 'none';  // Hide any previous errors
   resultsDiv.style.display = 'none';  // Hide any previous results

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
        }
        return response.json();
    })
    .then(recommendations => {
          if (recommendations.message) {
                errorMessageDiv.textContent = `An error occurred: ${recommendations.message}`;
                errorMessageDiv.style.display = 'block'; // Show the error message
               return;
            }
       const coursesList = document.querySelector('#courses ul');
       const videosList = document.querySelector('#videos ul');
       const jobsList = document.querySelector('#jobs ul');

       coursesList.innerHTML = '';
       videosList.innerHTML = '';
       jobsList.innerHTML = '';


       recommendations.courses.forEach(course => {
           const li = document.createElement('li');
           li.innerHTML = `<a href="${course.link}" target="_blank">${course.name}</a> (${course.platform})`;
           coursesList.appendChild(li);
       });

       recommendations.videos.forEach(video => {
           const li = document.createElement('li');
           li.innerHTML = `<a href="${video.link}" target="_blank">${video.name}</a> (${video.platform})`;
           videosList.appendChild(li);
        });

       recommendations.jobs.forEach(job => {
           const li = document.createElement('li');
           li.innerHTML = `<a href="${job.link}" target="_blank">${job.title}</a> at ${job.company}`;
            jobsList.appendChild(li);
       });

       resultsDiv.style.display = 'block'; // Show results
    })
     .catch(error => {
          console.error("Error:", error);
            errorMessageDiv.textContent = `An error occurred: ${error}`;
            errorMessageDiv.style.display = 'block'; // Show the error message
        });


});
