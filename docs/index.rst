Mixonomer
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Py <src/music>
   Js <src/MusicTools>
   Admin Script <src/admin>
   All Modules <src/modules>

`Mixonomer <https://music.sarsoo.xyz>`_
----------------------------------------------

.. image:: https://github.com/sarsoo/Mixonomer/workflows/test%20and%20deploy/badge.svg

Mixonomer is a web app for creating smart Spotify playlists. The app is based on `spotframework <https://github.com/Sarsoo/spotframework>`_ and `fmframework <https://github.com/Sarsoo/pyfmframework>`_ for interfacing with Spotify and Last.fm. The app is currently hosted on Google's Cloud Platform.

The backend is composed of a Flask web server with a Fireo ORM layer and longer tasks dispatched to Cloud Tasks or Functions. The frontend is a React app with material UI components and Axios for HTTP requests.

.. image:: Playlists.png


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
