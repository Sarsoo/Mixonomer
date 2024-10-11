import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import PlaylistsView from "./PlaylistsList.js"
import NewPlaylist from "./New.js";

/**
 * Router for playlist lists page, includes new playlist page
 */
class Playlists extends Component {
    render(){
        return (
            <div>                
                <Switch>

                    {/* PLAYLIST LIST */}
                    <Route exact path={`${this.props.match.url}/`} element={PlaylistsView} />

                    {/* NEW PLAYLIST */}
                    <Route path={`${this.props.match.url}/new`} element={NewPlaylist} />
                </Switch>
            </div>
        );
    }
}

export default Playlists;