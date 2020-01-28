import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";

import PlaylistsView from "./PlaylistsList.js"
import NewPlaylist from "./New.js";
import ScratchView from  "./ScratchView.js";

class Playlists extends Component {
    render(){
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/new`}>New</Link></li>
                    <li><Link to={`${this.props.match.url}/play`}>Play</Link></li>
                </ul>
                
                <Switch>
                    <Route exact path={`${this.props.match.url}/`} component={PlaylistsView} />
                    <Route path={`${this.props.match.url}/new`} component={NewPlaylist} />
                    <Route path={`${this.props.match.url}/play`} component={ScratchView} />
                </Switch>
            </div>
        );
    }
}

export default Playlists;