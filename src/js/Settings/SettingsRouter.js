import React, { Component } from "react";
import { Route, Link, Switch } from "react-router-dom";
import { Paper, Tabs, Tab} from '@material-ui/core';

import ChangePassword from "./ChangePassword.js";
import SpotifyLink from "./SpotifyLink.js";
import LastFM from "./LastFM.js";

/**
 * Settings card tabs structure for hosting password/spotify linked/last.fm username tabs
 */
class Settings extends Component {

    constructor(props){
        super(props);
        this.state = {
            tab: 0
        }
        this.handleChange = this.handleChange.bind(this);
    }

    /**
     * Handle tab change event
     * @param {*} e Event args
     * @param {*} newValue New tab object
     */
    handleChange(e, newValue){
        this.setState({
            tab: newValue
        });
    }

    render() {
        return (
            <div>
                <Paper>
                    <Tabs
                        value={this.state.tab}
                        onChange={this.handleChange}
                        indicatorColor="primary"
                        centered
                        width="50%"
                    >
                        {/* PASSWORD */}
                        <Tab label="Password" component={Link} to={`${this.props.match.url}/password`} />

                        {/* SPOTIFY */}
                        <Tab label="Spotify" component={Link} to={`${this.props.match.url}/spotify`} />

                        {/* LAST.FM */}
                        <Tab label="Last.fm" component={Link} to={`${this.props.match.url}/lastfm`} />
                    </Tabs>
                </Paper>                
                <Switch>

                    {/* PASSWORD */}
                    <Route path={`${this.props.match.url}/password`} component={ChangePassword} />

                    {/* SPOTIFY */}
                    <Route path={`${this.props.match.url}/spotify`} component={SpotifyLink} />

                    {/* LAST.FM */}
                    <Route path={`${this.props.match.url}/lastfm`} component={LastFM} />
                </Switch>
            </div>
        );
    }
}



export default Settings;