import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";

import ChangePassword from "./ChangePassword.js";
import SpotifyLink from "./SpotifyLink.js";

class Settings extends Component {

    render() {
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/password`}>password</Link></li>
                    <li><Link to={`${this.props.match.url}/spotify`}>spotify</Link></li>
                </ul>
                
                <Route path={`${this.props.match.url}/password`} component={ChangePassword} />
                <Route path={`${this.props.match.url}/spotify`} component={SpotifyLink} />

            </div>
        );
    }
}



export default Settings;