import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Index from "./Index.js";
import Settings from "./Settings.js";

class PlaylistManager extends Component {

    render(){
        return (
            <Router>
                <ul className="navbar">
                    <li><Link to="/app">home</Link></li>
                    <li><Link to="/app/settings">settings</Link></li>
                </ul>
                
                <Route path="/app" exact component={Index} />
                <Route path="/app/settings" component={Settings} />
            </Router>
        );
    }

}

export default PlaylistManager;