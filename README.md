[Mixonomer](https://mixonomer.sarsoo.xyz)
==================

![Python Tests](https://github.com/sarsoo/Mixonomer/workflows/test%20and%20deploy/badge.svg)

Smart playlists for Spotify with Last.fm insights. Mixonomer is a cloud native platform for combining Spotify playlists and enhancing them with recommendations and listening history data. I started the app in 2019, but Spotify have included similar features since then such as [enhanced playlists](https://www.theverge.com/2021/9/9/22664655/spotify-enhance-feature-recommended-songs-playlists) and [smart shuffle](https://newsroom.spotify.com/2023-03-08/smart-shuffle-new-life-spotify-playlists/). 

Built on my other libraries for Spotify ([spotframework](https://github.com/Sarsoo/spotframework)), Last.fm ([fmframework](https://github.com/Sarsoo/pyfmframework)) and interfacing utility tools for the two ([spotfm](https://github.com/Sarsoo/pyfmframework)). Currently running on a suite of Google Cloud Platform services. An iOS client is currently under development [here](https://github.com/Sarsoo/Mixonomer-iOS).

Read the full documentation [here](https://docs.mixonomer.sarsoo.xyz). Read the blog post [here](https://sarsoo.xyz/mixonomer/).

# Smart Playlists

Create smart playlists for Spotify including tracks from playlists, library and Spotify recommendations.

![Playlists List](docs/Playlists.png)
![Playlist Example](docs/PlaylistExample.png)

Playlists can pull tracks from multiple sources with some extra ones based on the playlist's type.

* Spotify playlists 
    - Currently referenced by case-sensitive names of those followed by the user
    - Plan to include reference by Spotify URI
* Other Mixonomer playlists
    - Dynamically include the Spotify playlists of other managed playlists
    - Used to allow hierarchy playlists such as for genre (as seen above for multiple rap playlists)
* Spotify Library Tracks
* Monthly Playlists
    - ONLY for "Recents" type playlists
    - Find user playlists by name in the format "month year" e.g. february 20 (lowercase)
    - Can dynamically include this month's and/or last month's playlist at runtime 
* Last.fm track chart data
    - ONLY for "Last.fm Chart" type playlists
    - Include variable number of top tracks in the last date range

When not shuffled, playlists are date sorted with newest at the top for a rolling album artwork of newest releases.

Playlists are updated using the [spotframework](https://github.com/Sarsoo/spotframework) playlist engine three times a day.

# Tags

Groups of Last.fm objects for summing of scrobble counts and listening statistics.

![Tag Example](docs/TagExample.png)

## Structure

This repo consists of a front-end written in React.js and Material-UI being served by a back-end written in Flask.

The application is hosted on Google Cloud Infrastructure.

## Acknowledgements

Took inspiration from Paul Lamere's [smarter playlists](http://smarterplaylists.playlistmachinery.com/).