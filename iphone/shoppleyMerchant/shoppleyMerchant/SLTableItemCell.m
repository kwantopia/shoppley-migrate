//
//  SLTableItemCell.m
//  shoppleyMerchant
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLTableItemCell.h"

#import <Three20Style/UIFontAdditions.h>
#import <Three20UI/UIViewAdditions.h>

#import "SLActiveOffer.h"
#import "SLAdditions.h"
#import "SLPastOffer.h"

@implementation SLActiveOfferTableItemCell

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    // TODO(yod): fix this
    //SLCurrentOfferTableItem* item = object;
    //SLCurrentOffer* offer = item.offer;
    return 90;
}

- (void)setObject:(id)object {
    if (_item != object) {
        self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
        self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
        
        SLActiveOfferTableItem* item = object;
        SLActiveOffer* offer = item.offer;
        
        if (offer.name.length) {
            self.titleLabel.text = offer.name;
        } else {
            self.titleLabel.text = @"";
        }
        if (offer.description.length) {
            self.detailTextLabel.text = offer.description;
        } else {
            self.detailTextLabel.text = @"";
        }
        if (offer.expires) {
            self.captionLabel.text = [NSString stringWithFormat:@"Expires: %@", [offer.expires formatFutureRelativeTime]];
            //self.timestampLabel.text = [item.timestamp formatShortTime];
        }
        if (offer.img) {
            self.imageView2.urlPath = offer.img;
        }
        if (offer.redeemedPercentage && offer.received) {
            self.timestampLabel.text = [NSString stringWithFormat:@"%@ (%.0f%%)", offer.received, [offer.redeemedPercentage floatValue]];
        }
    }
}

- (UILabel*)captionLabel {
    UILabel* captionLabel = [super captionLabel];
    captionLabel.textColor = [UIColor redColor];
    return captionLabel;
}

- (UILabel*)timestampLabel {
    if (!_timestampLabel) {
        [super timestampLabel];
        _timestampLabel.font = [UIFont boldSystemFontOfSize:14];
    }
    return _timestampLabel;
}

@end

@implementation SLPastOfferTableItemCell

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    // TODO(yod): fix this
     //SLCurrentOfferTableItem* item = object;
    // SLCurrentOffer* offer = item.offer;
     
    return 90;
}

- (void)setObject:(id)object {
    if (_item != object) {
        self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
        self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
        
        SLActiveOfferTableItem* item = object;
        SLActiveOffer* offer = item.offer;
        
        if (offer.name.length) {
            self.titleLabel.text = offer.name;
        } else {
            self.titleLabel.text = @"";
        }
        if (offer.description.length) {
            self.detailTextLabel.text = offer.description;
        } else {
            self.detailTextLabel.text = @"";
        }
        if (offer.expires) {
            self.captionLabel.text = [NSString stringWithFormat:@"Expired: %@", [offer.expires formatFullDateTime]];
            //self.timestampLabel.text = [item.timestamp formatShortTime];
        }
        if (offer.img) {
            self.imageView2.urlPath = offer.img;
        }
        if (offer.redeemedPercentage && offer.received) {
            self.timestampLabel.text = [NSString stringWithFormat:@"%@ (%.0f%%)", offer.received, [offer.redeemedPercentage floatValue]];
        }
    }
}

- (UILabel*)captionLabel {
    UILabel* captionLabel = [super captionLabel];
    captionLabel.textColor = [UIColor redColor];
    return captionLabel;
}

- (UILabel*)timestampLabel {
    if (!_timestampLabel) {
        [super timestampLabel];
        _timestampLabel.font = [UIFont boldSystemFontOfSize:14];
    }
    return _timestampLabel;
}

@end

@implementation SLRightValueTableItemCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString*)identifier {
    if ((self = [super initWithStyle:style reuseIdentifier:identifier])) {
        self.textLabel.font = TTSTYLEVAR(tableSmallFont);
        
        self.detailTextLabel.lineBreakMode = UILineBreakModeTailTruncation;
        self.detailTextLabel.numberOfLines = 1;
    }
    
    return self;
}

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    return 42;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    static CGFloat kValueWidth = 75;
    static CGFloat kValueSpacing = 12;
    
    CGFloat valueWidth = self.contentView.width - (kTableCellHPadding*2 + kValueWidth + kValueSpacing);
    //CGFloat innerHeight = self.contentView.height - kTableCellVPadding*2;
    
    self.textLabel.frame = CGRectMake(kTableCellHPadding + kValueSpacing + valueWidth, self.contentView.height - kTableCellVPadding - self.textLabel.font.ttLineHeight, kValueWidth, self.textLabel.font.ttLineHeight);
    self.detailTextLabel.frame = CGRectMake(kTableCellHPadding, self.contentView.height - kTableCellVPadding - self.detailTextLabel.font.ttLineHeight, valueWidth, self.detailTextLabel.font.ttLineHeight);
}

@end

@implementation SLStarsTableItemCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString*)identifier {
    if ((self = [super initWithStyle:style reuseIdentifier:identifier])) {
        self.accessoryType = UITableViewCellAccessoryNone;
        self.selectionStyle = TTSTYLEVAR(tableSelectionStyle);
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_item);
    [super dealloc];
}

- (id)object {
    return _item;
}

+ (CGFloat)tableView:(UITableView*)tableView rowHeightForObject:(id)object {
    return 100;
}

- (void)setObject:(id)object {
    if (_item != object) {
        [_item release];
        _item = [object retain];
        
        [self.contentView removeAllSubviews];
        
        CGFloat left = 10;
        for (int i = 0; i < [_item.numberOfStars intValue]; i++) {
            UIImageView* t = [[[UIImageView alloc] initWithFrame:CGRectMake(left, 5, 30, 30)] autorelease];
            t.image = [UIImage imageNamed:@"star30.png"];
            [self.contentView addSubview:t];
            
            left += 40;
        }
    }
}

- (void)layoutSubviews {
    [super layoutSubviews];
}

@end

@implementation SLRightStarsTableItemCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString*)identifier {
    if ((self = [super initWithStyle:style reuseIdentifier:identifier])) {
        _starsView = [[UIView alloc] init];
        [self.contentView addSubview:_starsView];
    }
    
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_starsView);
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    TTDPRINT(@"%e %e", self.contentView.height, _starsView.size.height);
    _starsView.frame = CGRectMake(self.contentView.width - _starsViewWidth, (self.contentView.height - 15) / 2, _starsViewWidth, 15);
}

- (void)setObject:(id)object {
    if (_item != object) {
        [super setObject:object];
        
        SLRightStarsTableItem* item = object;
        [_starsView removeAllSubviews];
        
        CGFloat left = 10;
        for (int i = 0; i < [item.numberOfStars intValue]; i++) {
            UIImageView* t = [[[UIImageView alloc] initWithFrame:CGRectMake(left, 0, 15, 15)] autorelease];
            t.image = [UIImage imageNamed:@"star15.png"];
            [_starsView addSubview:t];
            left += 18;
        }
        _starsViewWidth = left;
    }
}

@end
