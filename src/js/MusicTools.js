import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";

import NotFound from "./Error/NotFound.js";

import showMessage from "./Toast.js"

import GlobalTheme from './Theme.js';

import { Typography, CircularProgress } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';

import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import { Build, PieChart, QueueMusic, ExitToApp, AccountCircle, KeyboardBackspace, GroupWork } from '@material-ui/icons'

const axios = require('axios');

const LazyIndex = React.lazy(() => import("./Index/Index"))
const LazyPlaylists = React.lazy(() => import("./Playlist/AllPlaylistsRouter"))
const LazyPlaylistView = React.lazy(() => import("./Playlist/View/PlaylistRouter"))
const LazySettings = React.lazy(() => import("./Settings/SettingsRouter"))
const LazyAdmin = React.lazy(() => import("./Admin/AdminRouter"))
const LazyTags = React.lazy(() => import("./Tag/TagRouter"))
const LazyTag = React.lazy(() => import("./Tag/View"))

/**
 * Root component for app
 */
class MusicTools extends Component {

    constructor(props){
        super(props);
        this.state = {
            type: null,
            spotify_linked: null,
            drawerOpen: false
        }
        this.setOpen = this.setOpen.bind(this);
    }

    /**
     * Get user info from API on load
     */
    componentDidMount() {
        this.getUserInfo();
    }

    /**
     * Cancel get user info request
     */
    componentWillUnmount() {
        this.userInfoCancelToken.cancel();
    }

    /**
     * Get user info from API
     */
    getUserInfo(){
        this.userInfoCancelToken = axios.CancelToken.source();

        var self = this;
        axios.get('/api/user', {
            cancelToken: this.userInfoCancelToken.token
        })
        .then((response) => {
            self.setState({
                type: response.data.type,
                spotify_linked: response.data.spotify_linked
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    /**
     * Set whether side app drawer is open
     * @param {*} bool Open state of side drawer 
     */
    setOpen(bool){
        this.setState({
            drawerOpen: bool
        })
    }

    render(){
        return (
            <Router>
                <ThemeProvider theme={GlobalTheme}>

                    {/* TOP APP BAR */}

                    <AppBar position="static">
                        <Toolbar>
                            <IconButton edge="start" color="inherit" aria-label="menu" onClick={(e) => this.setOpen(true)}>
                            <MenuIcon />
                            </IconButton>
                            <Typography variant="h6">
                                <Link to='/app/playlists' style={{textDecoration: 'none'}}>Music Tools</Link>
                            </Typography>
                        </Toolbar>
                    </AppBar>

                    {/* MENU DRAWER */}
                    
                    <Drawer
                        variant="persistent"
                        anchor="left"
                        open={this.state.drawerOpen}
                        onClose={(e) => this.setOpen(false)}
                    >
                        <div>
                            <IconButton onClick={(e) => this.setOpen(false)}>
                                <ChevronLeftIcon />
                            </IconButton>
                        </div>
                        <Divider />
                        <div
                        role="presentation"
                        onClick={(e) => this.setOpen(false)}
                        onKeyDown={(e) => this.setOpen(false)}
                        >
                        <List>
                            {/* HOME */}
                            <ListItem button key="home" component={Link} to='/app'>
                                <ListItemIcon><HomeIcon /></ListItemIcon>
                                <ListItemText primary="Home" />
                            </ListItem>

                            {/* PLAYLISTS */}
                            <ListItem button key="playlists" component={Link} to='/app/playlists'>
                                <ListItemIcon><QueueMusic /></ListItemIcon>
                                <ListItemText primary="Playlists" />
                            </ListItem>

                            {/* TAGS */}
                            <ListItem button key="tags" component={Link} to='/app/tags'>
                                <ListItemIcon><GroupWork /></ListItemIcon>
                                <ListItemText primary="Tags" />
                            </ListItem>

                            {/* SETTINGS */}
                            <ListItem button key="settings" component={Link} to='/app/settings/password'>
                                <ListItemIcon><Build /></ListItemIcon>
                                <ListItemText primary="Settings" />
                            </ListItem>

                            {/* ADMIN */}
                            { this.state.type == 'admin' &&
                                <ListItem button key="admin" component={Link} to='/app/admin/lock'>
                                    <ListItemIcon><AccountCircle /></ListItemIcon>
                                    <ListItemText primary="Admin" />
                                </ListItem>
                            }

                            {/* LOGOUT */}
                            <ListItem button key="logout" onClick={(e) => { window.location.href = '/auth/logout' }}>
                                <ListItemIcon><KeyboardBackspace /></ListItemIcon>
                                <ListItemText primary="Logout" />
                            </ListItem>

                            {/* SARSOO.XYZ */}
                            <ListItem button key="sarsoo.xyz" onClick={(e) => { window.location.href = 'https://sarsoo.xyz' }}>
                                <ListItemIcon><ExitToApp /></ListItemIcon>
                                <ListItemText primary="sarsoo.xyz" />
                            </ListItem>
                        </List>
                        </div>
                    </Drawer>
                    
                    {/* ROUTER SWITCH */}

                    <div className="full-width">
                        <Switch>
                            <React.Suspense fallback={<LoadingMessage/>}>
                                <Route path="/app" exact component={LazyIndex} />
                                <Route path="/app/playlists" component={LazyPlaylists} />
                                <Route path="/app/tags" component={LazyTags} />
                                <Route path="/app/tag/:tag_id" component={LazyTag} />
                                <Route path="/app/settings" component={LazySettings} />
                                { this.state.type == 'admin' && <Route path="/app/admin" component={LazyAdmin} /> }
                                <Route path='/app/playlist/:name' component={LazyPlaylistView} />
                            </React.Suspense>
                            <Route component={NotFound} />
                        </Switch>
                    </div>
                </ThemeProvider>
            </Router>
        );
    }

}

function LoadingMessage(props) {
    return <CircularProgress/>;
}

export default MusicTools;