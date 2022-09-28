# Module 1 Group Assignment

CSCI 5117, Spring 2022, [assignment description](https://canvas.umn.edu/courses/291031/pages/project-1)

## App Info:

* Team Name: Full-Stack-Overflow
* App Name: MediaMadness
* App Link: <https://media-madness-5117.herokuapp.com/>

### Students

* Rayan Dhamuke, dhamu002@umn.edu
* Hung DoVu, dovu0001@umn.edu
* Sami Hammami, hamma212@umn.edu
* Michael McCune, mccun050@umn.edu
* Dongwei Pan, pan00179@umn.edu


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* The "Home" page determines and shows the most popular media in each watchlist category on MediaMadness
* The "MediaInfo" page has general information from TMDB's API, watchlist counts for MediaMadness, ability to modify watchlists quickly, and compiles other users who have media added to watchlist.
* The "Profile" page allows users to modify watchlists quickly through drag-and-drop.
* The "Community" page determines and shows the most similar users to yourself based on watchlists or the most active users in each watchlist category.



## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* Non-logged in users can search and browse for media, can't add anything to lists, get similar user recommendations, or follow others.
* For each user, there cannot be any duplicate medias between the Watched, Watching, and Want to Watch lists.
* For some media in the search results page, there is missing information such as a missing poster, or no cast list is provided. This is due to TMDB not having that information about the media.


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**

<!-- ![](https://media.giphy.com/media/o0vwzuFwCGAFO/giphy.gif) -->

### Home Page
##### The "Home" page displays the most popular media in each watchlist category on MediaMadness.
<img width="1680" alt="Home Page" src="https://user-images.githubusercontent.com/98062900/159626776-acf179f7-6b7f-4a0b-95a4-9eaf10251607.png">


### MediaInfo Page
##### The "MediaInfo" page shows more detailed information about specific media.
<img width="1680" alt="MediaInfo Page" src="https://user-images.githubusercontent.com/98062900/159626967-522bbf1f-b6a7-4c94-b682-ebfbb4c24a88.png">

### Profile Page
##### The "Profile" page shows all watchlists for a user along with a bio.
<img width="1680" alt="Profile Page" src="https://user-images.githubusercontent.com/98062900/159627059-a0106432-93dd-4333-bd33-ab2b5bf2a384.png">

### Community Page
##### The "Community" page displays either recommended users or shows the most popular users in each watchlist category.
<img width="1680" alt="Community Page" src="https://user-images.githubusercontent.com/98062900/159627100-c9e889e9-7974-407b-83b0-6c1359b28dcb.png">


## Mock-up 

https://balsamiq.cloud/s3yfvw0/p7g1otw


## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* TMDB API: The TMDB API was used to gather media data to be displayed on the site (title, poster, description, cast, ratings)

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

N/A
