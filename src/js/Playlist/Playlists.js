import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

import PlaylistsView from "./PlaylistsView.js"

class Playlists extends Component {
    render(){
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/add`}>add</Link></li>
                </ul>
                
                <Route path={`${this.props.match.url}/`} component={PlaylistsView} />

            </div>
        );
    }
}

export default Playlists;