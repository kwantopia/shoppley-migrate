//
//  OfferDetailViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferDetailViewController.h"

#import "SLActiveOffer.h"
#import "SLAdditions.h"
#import "SLDataController.h"
#import "SLNewOffer.h"
#import "SLPastOffer.h"
#import "SLTableViewDataSource.h"
#import "SLTableItem.h"

@implementation OfferDetailViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [super init])) {
        _offer = [[query objectForKey:@"offer"] retain];
        self.title = _offer.name;
           
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
        
        _isActiveOffer = [_offer isKindOfClass:[SLActiveOffer class]];
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

- (void)createModel {
    NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
    NSMutableArray* sections = [[[NSMutableArray alloc] init] autorelease];
    
    NSMutableArray* stats = [[[NSMutableArray alloc] init] autorelease];
    [stats addObject:[SLRightValueTableItem itemWithText:@"Sent to" value:[NSString stringWithFormat:@"%@", _offer.received]]];
    [stats addObject:[SLRightValueTableItem itemWithText:@"Redeemed" value:[NSString stringWithFormat:@"%@", _offer.redeemed]]];
    if ([_offer.received intValue] > 0) {
        [stats addObject:[SLRightValueTableItem itemWithText:@"Percentage" value:[NSString stringWithFormat:@"%.2f%%", [_offer.redeemedPercentage floatValue]]]];
    }
    [items addObject:stats];
    [sections addObject:@""];

    self.dataSource = [SLSectionedDataSource dataSourceWithItems:items sections:sections];
    
    TTButton* button;
    bool hasButton = NO;
    if (_isActiveOffer && [((SLActiveOffer*)_offer).redistributable boolValue]) {
        button = [TTButton buttonWithStyle:@"greenButton:" title:@"Send More"];
        [button addTarget:self action:@selector(sendMoreOffersClicked) forControlEvents:UIControlEventTouchUpInside];
        hasButton = YES;
    } else if (!_isActiveOffer) {
        button = [TTButton buttonWithStyle:@"greenButton:" title:@"Restart Offer"];
        [button addTarget:self action:@selector(restartOffer) forControlEvents:UIControlEventTouchUpInside];
        hasButton = YES;
    }
    
    if (hasButton) {
        button.enabled = YES;
        [button sizeToFit];
        button.frame = CGRectMake(10, 10, self.view.frame.size.width - 20, button.frame.size.height);
        UIView* footerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, button.frame.size.height + 10)] autorelease];
        [footerView addSubview:button];
        self.tableView.tableFooterView = footerView;
    } else {
        self.tableView.tableFooterView = NULL;
    }
}

- (void)viewWillAppear:(BOOL)animated {
    [self createModel];
    
    UIView* headerView = [[[OfferDetailHeaderView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, 50) offer:_offer] autorelease];
    self.tableView.tableHeaderView = headerView;
    [super viewWillAppear:animated];
}

#pragma mark send more offers

- (void)sendMoreOffersClicked {
    self.tableView.tableFooterView = NULL;
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    [self performSelectorInBackground:@selector(sendMoreOffers) withObject:self];
}

- (void)sendMoreOffersDone:(NSDictionary*)result {
    [_offer populateFromDictionary:[result objectForKey:@"offer"]];
    [self createModel];
}

- (void)sendMoreOffersFailed {
    [self createModel];
}

- (void)sendMoreOffers {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    
    NSDictionary* result = [[SLDataController sharedInstance] sendMoreWithOfferId:_offer.offerId];
    
    if (result != NULL) {
        UIAlertView *alert = [[[UIAlertView alloc]
                              initWithTitle:@""
                              message:@"Successfully sent a request."
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil] autorelease];
        [alert show];
        [self performSelectorOnMainThread:@selector(sendMoreOffersDone:) withObject:result waitUntilDone:NO];
    } else {
        UIAlertView *alert = [[[UIAlertView alloc]
                              initWithTitle:@""
                              message:[SLDataController sharedInstance].errorString
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil] autorelease];
        [alert show];
        [self performSelectorOnMainThread:@selector(sendMoreOffersFailed) withObject:nil waitUntilDone:NO];
    }
    
    [pool release];
}

#pragma mark restart offer

- (void)restartOffer {
    SLNewOffer* offer = [[[SLNewOffer alloc] init] autorelease];
    offer.name = _offer.name;
    offer.description = _offer.description;
    if ([_offer isKindOfClass:[SLPastOffer class]]) {
        offer.duration = ((SLPastOffer*)_offer).duration;
        offer.amount = ((SLPastOffer*)_offer).amount;
        offer.unit = ((SLPastOffer*)_offer).unit;
    }
    
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer/new"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:offer forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

@end

@implementation OfferDetailHeaderView

- (id)initWithFrame:(CGRect)frame offer:(SLOffer*)offer {
    if ((self = [super initWithFrame:frame])) {
        static const CGFloat kImageWidth = 50;
        static const CGFloat kImageHeight = 50;
        static const CGFloat kSmallMargin = 7;
        static const CGFloat kLargeMargin = 10;
        
        self.backgroundColor = [UIColor clearColor];
        
        BOOL isActiveOffer = [offer isKindOfClass:[SLActiveOffer class]];
        
        TTImageView* imageView = [[[TTImageView alloc] init] autorelease];
        imageView.urlPath = offer.img;        
        imageView.frame = CGRectMake(kSmallMargin, kSmallMargin, kImageWidth, kImageHeight);
        [self addSubview:imageView];
        
        CGFloat left = kSmallMargin + kImageWidth + kLargeMargin;
        
        TTStyledTextLabel* titleLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(left, kSmallMargin, frame.size.width - left - kSmallMargin, 100)] autorelease];
        titleLabel.font = [UIFont systemFontOfSize:17];
        NSString* title = [NSString stringWithFormat:@"<b>%@</b>", offer.name];
        titleLabel.text = [TTStyledText textFromXHTML:title lineBreaks:YES URLs:YES];
        titleLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [titleLabel sizeToFit];
        titleLabel.backgroundColor = self.backgroundColor;
        [self addSubview:titleLabel];
        
        CGFloat top = kSmallMargin + MAX(titleLabel.frame.size.height, kImageHeight) + kLargeMargin;
        TTStyledTextLabel* detailLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        detailLabel.font = [UIFont systemFontOfSize:14];
        NSString* detail = offer.description;
        detailLabel.text = [TTStyledText textFromXHTML:detail lineBreaks:YES URLs:YES];
        detailLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [detailLabel sizeToFit];
        detailLabel.backgroundColor = self.backgroundColor;
        [self addSubview:detailLabel];
        
        top += detailLabel.frame.size.height + kSmallMargin;
        
        TTStyledTextLabel* redLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        redLabel.font = [UIFont systemFontOfSize:14];
        NSString* redLabelText = @"";
        if (isActiveOffer) {
            redLabelText = [NSString stringWithFormat:@"<span class=\"redText\"><b>expires: %@</b></span>", [offer.expires formatFullDateTime]];
        } else {
            redLabelText = [NSString stringWithFormat:@"<span class=\"redText\"><b>Expired on: %@</b></span>", [offer.expires formatFullDateTime]];
        }
        redLabel.text = [TTStyledText textFromXHTML:redLabelText lineBreaks:YES URLs:YES];
        redLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [redLabel sizeToFit];
        redLabel.backgroundColor = self.backgroundColor;
        [self addSubview:redLabel];
        
        top += redLabel.frame.size.height;

        // Resize
        frame.size.height = top + kLargeMargin;
        self.frame = frame;
    }
    return self;
}

@end
