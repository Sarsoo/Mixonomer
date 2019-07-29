import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Index from "./Index.js";
import Playlists from "./Playlist/Playlists.js";
import PlaylistView from "./Playlist/PlaylistView.js";
import Settings from "./Settings.js";

class PlaylistManager extends Component {

    render(){
        return (
            <Router>
                <div className="card pad-12">
                    <ul className="sidebar pad-3">
                        <li><Link to="/app">home</Link></li>
                        <li><Link to="/app/playlists">playlists</Link></li>
                        <li><Link to="/app/settings">settings</Link></li>
                        <li><a href="/auth/logout">logout</a></li>
                        <li><a href="https://sarsoo.xyz">sarsoo.xyz</a></li>
                    </ul>

                    <div className="pad-9">
                        <Route path="/app" exact component={Index} />
                        <Route path="/app/playlists" exact component={Playlists} />
                        <Route path="/app/settings" component={Settings} />
                    </div>
                </div>
                
            </Router>
        );
    }

}

export default PlaylistManager;