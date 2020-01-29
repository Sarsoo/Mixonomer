import React, { Component } from "react";
import { Route, Link, Switch } from "react-router-dom";
import { Paper, Tabs, Tab} from '@material-ui/core';

import ChangePassword from "./ChangePassword.js";
import SpotifyLink from "./SpotifyLink.js";
import LastFM from "./LastFM.js";

class Settings extends Component {

    constructor(props){
        super(props);
        this.state = {
            tab: 0
        }
        this.handleChange = this.handleChange.bind(this);
    }

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
                        <Tab label="Password" component={Link} to={`${this.props.match.url}/password`} />
                        <Tab label="Spotify" component={Link} to={`${this.props.match.url}/spotify`} />
                        <Tab label="Last.fm" component={Link} to={`${this.props.match.url}/lastfm`} />
                    </Tabs>
                </Paper>                
                <Switch>
                    <Route path={`${this.props.match.url}/password`} component={ChangePassword} />
                    <Route path={`${this.props.match.url}/spotify`} component={SpotifyLink} />
                    <Route path={`${this.props.match.url}/lastfm`} component={LastFM} />
                </Switch>
            </div>
        );
    }
}



export default Settings;