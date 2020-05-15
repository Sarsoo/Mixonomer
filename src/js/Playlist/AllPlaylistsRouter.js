import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import PlaylistsView from "./PlaylistsList.js"
import NewPlaylist from "./New.js";

class Playlists extends Component {
    render(){
        return (
            <div>                
                <Switch>
                    <Route exact path={`${this.props.match.url}/`} component={PlaylistsView} />
                    <Route path={`${this.props.match.url}/new`} component={NewPlaylist} />
                </Switch>
            </div>
        );
    }
}

export default Playlists;