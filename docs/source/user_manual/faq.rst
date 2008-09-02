##########################
Frequently Asked Questions
##########################

.. contents::


Where does the name "Chaco" come from?
======================================

It is named after `Chaco Canyon <http://www.nps.gov/chcu/>`_, which had
astronomical markings that served as an observatory for Native Americans. The
original version of Chaco was built as part of a project for the `Space
Telescope Science Institute <http://www.stsci.edu/resources/>`_. This is also
the origin of the name "Kiva" for our vector graphics layer that Chaco uses for
rendering.


Why was Chaco named "Chaco2" for a while?
=========================================

Starting in January of 2006, we refactored and reimplemented much of the core
Chaco API. The effort has been named "chaco2", and lives in the
:mod:`enthought.chaco2` namespace. During that time, the original chaco package ("Chaco
Classic") was in maintenance-only mode, but there was still code that needed
features from both Chaco Classic and Chaco2.  That code has finally been either
shelved or refactored, and the latest versions of Chaco (3.0 and up) are back
to residing in the :mod:`enthought.chaco` namespace.  We still have compatibility
modules in :mod:`enthought.chaco2`, but they just proxy for the real code in
:mod:`enthought.chaco`.

The same applies to the :mod:`enthought.enable` and :mod:`enthought.enable2`
packages.


What are the pros and cons of Chaco vs. matplotlib?
===================================================

This question comes up quite a bit.  The bottom line is that the two projects
initially set out to do different things, and although each project has grown a
lot of overlapping features, the different original charters are reflected in
the capabilities and feature sets of the two projects.


Here is an `excerpt from a thread about this question
<https://mail.enthought.com/pipermail/enthought-dev/2007-May/005363.html>`_ on
the enthought-dev mailing list.

Gael Varoquaux's response::

    On Fri, May 11, 2007 at 10:03:21PM +0900, Bill Baxter wrote:

    > Just curious.  What are the pros and cons of chaco vs matplotlib?

    To me it seem the big pro of chaco is that it is much easier to use in a
    "programatic way" (I have no clue this means something in English). It is
    fully traited and rely quite a lot on inversion of control (sorry, I love
    this concept, so it has become my new buzz-word). You can make very nice
    object oriented interactive code.

    Another nice aspect is that it is much faster than MPL.

    The cons are that it is not as fully featured as MPL, that it does not
    has an as nice interactively useable functional interface (ie chaco.shell
    vs pylab) and that it is not as well documented and does not have the
    same huge community.

    I would say that the codebase of chaco is nicer, but than if you are not
    developping interactive application, it is MPL is currently an option
    that is lickely to get you where you want to go quicker. Not that I
    wouldn't like to see chaco building up a bit more and becoming **the** reference.

    Developers, if you want chaco to pick up momentum, give it a pylab-like
    interface (as close as you can to pylab) !

    My 2 cents,
    Gael


Peter Wang's response (excerpt)::

	On May 11, 2007, at 8:03 AM, Bill Baxter wrote:

    > Just curious.  What are the pros and cons of chaco vs matplotlib?
	
    You had to go and ask, didn't you? :)  There are many more folks here  
    who have used MPL more extensively than myself, so I'll defer the  
    comparisons to them.  (Gael, as always, thanks for your comments and  
    feedback!)  I can comment, however, on the key goals of Chaco.

    Chaco is a plotting toolkit targeted towards developers for building  
    interactive visualizations.  You hook up pieces to build a plot that  
    is then easy to inspect, interact with, add configuration UIs for  
    (using Traits UI), etc.  The layout of plot areas, the multiplicity  
    and types of renderers within those windows, the appearance and  
    locations of axes, etc. are all completely configurable since these  
    are all first-class objects participating in a visual canvas.  They  
    can all receive mouse and keyboard events, and it's easy to subclass  
    them (or attach tools to them) to achieve new kinds of behavior.   
    We've tried to make all the plot renderers adhere to a standard  
    interface, so that tools and interactors can easily inspect data and  
    map between screen space and data space.  Once these are all hooked  
    up, you can swap out or update the data independently of the plots.

    One of the downsides we had a for a while was that this rich set of  
    objects required the programmer to put several different classes  
    together just to make a basic plot.  To solve this problem, we've  
    assembled some higher-level classes that have the most common  
    behaviors built-in by default, but which can still be easily  
    customized or extended.  It's clear to me that this is a good general  
    approach to preserving flexibility while reducing verbosity.

    At this point, Chaco is definitely capable of handling a large number  
    of different plotting tasks, and a lot of them don't require too much  
    typing or hacking skills.  (Folks will probably require more  
    documentation, however, but I'm working on that. :)  I linked to the  
    source for all of the screenshots in the gallery to demonstrate that  
    you can do a lot of things with Chaco in a few dozen lines of code.   
    (For instance, the audio spectrogram at the bottom of the gallery is  
    just a little over 100 lines.)

    Fundamentally, I like the Chaco model of plots as compositions of  
    interactive components.  This really helps me think about  
    visualization apps in a modular way, and it "fits my head".  (Of  
    course, the fact that I wrote much of it might have something to do  
    with that as well. ;)  The goal is to have data-related operations  
    clearly happen in one set of objects, the view layout and  
    configuration happen in another, and the interaction controls fit  
    neatly into a third.  IMHO a good toolkit should help me design/ 
    architect my application better, and we definitely aspire to make  
    Chaco meet that criterion.

    Finally, one major perk is that since Chaco is built completely on  
    top of traits and its event-based component model, you can call  
    edit_traits() on any visual component from within your app (or  
    ipython) and get a live GUI that lets you tweak all of its various  
    parameters in realtime.  This applies to the axis, grid, renderers,  
    etc.  This seems so natural to me that I sometimes forget what an  
    awesome feature it is. :)  



