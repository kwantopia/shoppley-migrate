//
//  OffersViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OffersViewController.h"


@implementation OffersViewController

- (void)dealloc {
    TT_RELEASE_SAFELY(_offers);
    [super dealloc];
}

- (void)didFinishDownload {
    [self createModel];
}

- (void)didFailDownload {
    TTDPRINT(@"failed");
}

- (void)didSelectObject:(id)object atIndexPath:(NSIndexPath*)indexPath {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:[_offers objectAtIndex:[indexPath row]] forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

@end