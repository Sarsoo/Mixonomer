Music Tools
=======================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Modules <src/modules>
   src/music
   src/music.api
   src/music.auth
   src/music.cloud
   src/music.db
   src/music.model
   src/music.tasks
   src/MusicTools

`Music Tools <https://music.sarsoo.xyz>`_
----------------------------------------------

.. image:: https://github.com/sarsoo/music-tools/workflows/test%20and%20deploy/badge.svg

Music Tools is a web app for creating smart Spotify playlists. The app is based on `spotframework <https://github.com/Sarsoo/spotframework>`_ and `fmframework <https://github.com/Sarsoo/pyfmframework>`_ for interfacing with Spotify and Last.fm. The app is currently hosted on Google's Cloud Platform.

The system is composed of a Flask web server with a Fireo ORM layer and longer tasks dispatched to Cloud Tasks or Functions.

.. image:: Playlists.png


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
